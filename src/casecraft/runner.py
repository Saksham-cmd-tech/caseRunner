"""
runner.py — Asynchronous polyglot subprocess executor.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

from casecraft.models import TestCase, TestResult, Verdict
from casecraft.utils import normalize_output

DEFAULT_TIMEOUT: float = 2.0

async def compile_code(file_path: Path) -> tuple[bool, Optional[str], Optional[Path]]:
    """Compile code if necessary (C++, Java, Rust). Returns (success, error_msg, executable_path)"""
    ext = file_path.suffix.lower()
    
    if ext in ('.py', '.js', '.sh'):
        # No compilation needed
        return True, None, file_path
        
    temp_dir = Path(tempfile.gettempdir()) / "casecraft_builds"
    temp_dir.mkdir(exist_ok=True)
    
    if ext == '.cpp' or ext == '.cc':
        exe_path = temp_dir / file_path.stem
        # Ensure executable doesn't accidentally collide
        exe_path = exe_path.with_name(f"{file_path.stem}_{hash(str(file_path.resolve()))}")
        
        proc = await asyncio.create_subprocess_exec(
            "g++", "-O3", "-std=c++17", str(file_path), "-o", str(exe_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            return False, stderr.decode().strip(), None
        return True, None, exe_path
        
    elif ext == '.java':
        # Compile Java
        proc = await asyncio.create_subprocess_exec(
            "javac", str(file_path), "-d", str(temp_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            return False, stderr.decode().strip(), None
        return True, None, temp_dir # For Java, return dir
        
    # Default fallback
    return True, None, file_path

def get_run_command(file_path: Path, executable_path: Path) -> list[str]:
    ext = file_path.suffix.lower()
    if ext == '.py':
        python_cmd = "python" if os.name == "nt" else "python3"
        return [python_cmd, str(file_path)]
    elif ext == '.js':
        return ["node", str(file_path)]
    elif ext in ('.cpp', '.cc'):
        return [str(executable_path)]
    elif ext == '.java':
        return ["java", "-cp", str(executable_path), file_path.stem]
    else:
        # Fallback 
        return ["./" + file_path.name]

async def run_test_case_async(
    file_path: str,
    executable_path: Path,
    test_case: TestCase,
    timeout_seconds: float = DEFAULT_TIMEOUT,
) -> TestResult:
    path = Path(file_path)
    
    cmd = get_run_command(path, executable_path)
    
    start = time.perf_counter()
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=path.parent
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=test_case.input_data.encode()),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return TestResult(
                test_case=test_case,
                verdict=Verdict.TIME_LIMIT_EXCEEDED,
                runtime_ms=timeout_seconds * 1000,
                actual_output="",
                error="Execution timed out.",
                timed_out=True,
            )
            
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        stdout_str = stdout.decode('utf-8', errors='replace')
        stderr_str = stderr.decode('utf-8', errors='replace').strip()
        
        if proc.returncode != 0:
            return TestResult(
                test_case=test_case,
                verdict=Verdict.RUNTIME_ERROR,
                runtime_ms=elapsed_ms,
                actual_output=stdout_str,
                error=stderr_str,
                timed_out=False,
            )
            
        verdict = (
            Verdict.ACCEPTED
            if normalize_output(stdout_str) == normalize_output(test_case.expected_output)
            else Verdict.WRONG_ANSWER
        )
        
        return TestResult(
            test_case=test_case,
            verdict=verdict,
            runtime_ms=elapsed_ms,
            actual_output=stdout_str,
            error=None,
            timed_out=False,
        )
        
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return TestResult(
            test_case=test_case,
            verdict=Verdict.RUNTIME_ERROR,
            runtime_ms=elapsed_ms,
            actual_output="",
            error=str(exc),
            timed_out=False,
        )

async def run_all_test_cases_async(
    file_path: str,
    test_cases: list[TestCase],
    timeout_seconds: float = DEFAULT_TIMEOUT,
    progress_callback = None
) -> list[TestResult]:
    """Run all test cases concurrently after single compilation."""
    path = Path(file_path)
    
    if not path.exists():
        err_res = [
            TestResult(tc, Verdict.RUNTIME_ERROR, 0.0, "", f"File not found: {file_path}", False)
            for tc in test_cases
        ]
        if progress_callback:
            for r in err_res:
                progress_callback(r)
        return err_res
        
    # Compile
    success, err_msg, exe_path = await compile_code(path)
    if not success:
        err_res = [
            TestResult(tc, Verdict.COMPILATION_ERROR, 0.0, "", err_msg or "Compilation failed", False)
            for tc in test_cases
        ]
        if progress_callback:
            for r in err_res:
                progress_callback(r)
        return err_res
        
    # Execute concurrently
    async def run_and_notify(tc: TestCase):
        res = await run_test_case_async(file_path, exe_path, tc, timeout_seconds)
        if progress_callback:
            progress_callback(res)
        return res
        
    tasks = [asyncio.create_task(run_and_notify(tc)) for tc in test_cases]
    results = await asyncio.gather(*tasks)
    return results
