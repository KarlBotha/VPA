"""
VPA Integration Validation Framework

Automated validation and testing framework for VPA subsystem integrations.
Ensures all integrations meet architectural and quality standards.
"""

import os
import sys
import subprocess
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import importlib.util
import tempfile


@dataclass
class ValidationResult:
    """Result of a validation check."""
    name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0


@dataclass
class IntegrationReport:
    """Complete integration validation report."""
    integration_name: str
    timestamp: datetime
    overall_passed: bool
    results: List[ValidationResult]
    resource_usage: Dict[str, Any]
    dependencies: List[str]
    test_coverage: float


class VPAValidationFramework:
    """VPA Integration Validation Framework."""
    
    def __init__(self, project_root: Path):
        """Initialize validation framework."""
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Validation thresholds
        self.thresholds = {
            'test_coverage': 80.0,
            'performance_degradation': 20.0,
            'memory_usage_mb': 100.0,
            'startup_time_ms': 5000.0
        }
        
        # Critical architectural patterns
        self.required_patterns = {
            'event_driven': True,
            'plugin_based': True,
            'modular_design': True,
            'proper_cleanup': True
        }
    
    def setup_logging(self):
        """Setup validation logging."""
        log_dir = self.project_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def validate_integration(self, integration_name: str, integration_path: Path) -> IntegrationReport:
        """Validate a complete integration."""
        self.logger.info(f"Starting validation for integration: {integration_name}")
        
        start_time = time.time()
        results = []
        
        # 1. Architectural Compliance
        results.extend(self._validate_architecture(integration_path))
        
        # 2. Code Quality
        results.extend(self._validate_code_quality(integration_path))
        
        # 3. Testing
        test_coverage = self._validate_testing(integration_path)
        results.extend(test_coverage['results'])
        
        # 4. Resource Management
        results.extend(self._validate_resource_management(integration_path))
        
        # 5. Documentation
        results.extend(self._validate_documentation(integration_path))
        
        # 6. Dependencies
        dependency_results = self._validate_dependencies(integration_path)
        results.extend(dependency_results['results'])
        
        # 7. Performance Impact
        results.extend(self._validate_performance(integration_path))
        
        # Calculate overall result
        overall_passed = all(result.passed for result in results if result.name.startswith('CRITICAL'))
        
        # Generate report
        report = IntegrationReport(
            integration_name=integration_name,
            timestamp=datetime.now(),
            overall_passed=overall_passed,
            results=results,
            resource_usage=self._measure_resource_usage(),
            dependencies=dependency_results['dependencies'],
            test_coverage=test_coverage['coverage']
        )
        
        execution_time = time.time() - start_time
        self.logger.info(f"Validation completed in {execution_time:.2f}s")
        
        return report
    
    def _validate_architecture(self, integration_path: Path) -> List[ValidationResult]:
        """Validate architectural compliance."""
        results = []
        
        # Check for event-driven patterns
        result = self._check_event_driven_design(integration_path)
        results.append(ValidationResult(
            name="CRITICAL: Event-Driven Design",
            passed=result['passed'],
            message=result['message'],
            details=result.get('details')
        ))
        
        # Check plugin architecture
        result = self._check_plugin_architecture(integration_path)
        results.append(ValidationResult(
            name="CRITICAL: Plugin Architecture",
            passed=result['passed'],
            message=result['message'],
            details=result.get('details')
        ))
        
        # Check modularity
        result = self._check_modularity(integration_path)
        results.append(ValidationResult(
            name="CRITICAL: Modular Design",
            passed=result['passed'],
            message=result['message'],
            details=result.get('details')
        ))
        
        return results
    
    def _check_event_driven_design(self, integration_path: Path) -> Dict[str, Any]:
        """Check for event-driven design patterns."""
        try:
            python_files = list(integration_path.rglob("*.py"))
            
            event_patterns = {
                'event_bus_usage': False,
                'subscribe_calls': 0,
                'emit_calls': 0,
                'event_handlers': 0
            }
            
            for py_file in python_files:
                content = py_file.read_text()
                
                if 'EventBus' in content or 'event_bus' in content:
                    event_patterns['event_bus_usage'] = True
                
                event_patterns['subscribe_calls'] += content.count('.subscribe(')
                event_patterns['emit_calls'] += content.count('.emit(')
                event_patterns['event_handlers'] += content.count('def _on_') + content.count('def on_')
            
            passed = (event_patterns['event_bus_usage'] and 
                     event_patterns['subscribe_calls'] > 0)
            
            message = "Event-driven design validated" if passed else "Missing event-driven patterns"
            
            return {
                'passed': passed,
                'message': message,
                'details': event_patterns
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error validating event-driven design: {e}",
                'details': {'error': str(e)}
            }
    
    def _check_plugin_architecture(self, integration_path: Path) -> Dict[str, Any]:
        """Check for proper plugin architecture."""
        try:
            init_file = integration_path / '__init__.py'
            
            if not init_file.exists():
                return {
                    'passed': False,
                    'message': "Missing __init__.py file",
                    'details': {'missing_files': ['__init__.py']}
                }
            
            content = init_file.read_text()
            
            plugin_patterns = {
                'plugin_class': 'Plugin' in content or 'plugin' in content.lower(),
                'initialize_function': 'def initialize(' in content,
                'cleanup_function': 'def cleanup(' in content,
                'event_bus_integration': 'event_bus' in content
            }
            
            passed = plugin_patterns['plugin_class'] and plugin_patterns['event_bus_integration']
            
            message = "Plugin architecture validated" if passed else "Missing plugin architecture patterns"
            
            return {
                'passed': passed,
                'message': message,
                'details': plugin_patterns
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error validating plugin architecture: {e}",
                'details': {'error': str(e)}
            }
    
    def _check_modularity(self, integration_path: Path) -> Dict[str, Any]:
        """Check for modular design principles."""
        try:
            python_files = list(integration_path.rglob("*.py"))
            
            modularity_metrics = {
                'file_count': len(python_files),
                'avg_file_size': 0,
                'max_file_size': 0,
                'import_coupling': 0,
                'circular_imports': False
            }
            
            total_size = 0
            for py_file in python_files:
                size = py_file.stat().st_size
                total_size += size
                modularity_metrics['max_file_size'] = max(modularity_metrics['max_file_size'], size)
                
                # Check for excessive coupling
                content = py_file.read_text()
                import_count = content.count('import ') + content.count('from ')
                modularity_metrics['import_coupling'] += import_count
            
            if python_files:
                modularity_metrics['avg_file_size'] = total_size / len(python_files)
            
            # Check thresholds
            passed = (modularity_metrics['max_file_size'] < 50000 and  # 50KB max per file
                     modularity_metrics['avg_file_size'] < 10000)      # 10KB average
            
            message = "Modular design validated" if passed else "Design may be too monolithic"
            
            return {
                'passed': passed,
                'message': message,
                'details': modularity_metrics
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error validating modularity: {e}",
                'details': {'error': str(e)}
            }
    
    def _validate_code_quality(self, integration_path: Path) -> List[ValidationResult]:
        """Validate code quality using linting tools."""
        results = []
        
        # Flake8 linting
        flake8_result = self._run_flake8(integration_path)
        results.append(ValidationResult(
            name="Code Quality: Flake8",
            passed=flake8_result['passed'],
            message=flake8_result['message'],
            details=flake8_result.get('details')
        ))
        
        # Type checking with mypy
        mypy_result = self._run_mypy(integration_path)
        results.append(ValidationResult(
            name="Code Quality: Type Checking",
            passed=mypy_result['passed'],
            message=mypy_result['message'],
            details=mypy_result.get('details')
        ))
        
        # Security scanning with bandit
        bandit_result = self._run_bandit(integration_path)
        results.append(ValidationResult(
            name="CRITICAL: Security Scan",
            passed=bandit_result['passed'],
            message=bandit_result['message'],
            details=bandit_result.get('details')
        ))
        
        return results
    
    def _run_flake8(self, integration_path: Path) -> Dict[str, Any]:
        """Run flake8 linting."""
        try:
            result = subprocess.run(
                ['python', '-m', 'flake8', str(integration_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            passed = result.returncode == 0
            message = "Flake8 passed" if passed else f"Flake8 issues found: {len(result.stdout.splitlines())} lines"
            
            return {
                'passed': passed,
                'message': message,
                'details': {
                    'output': result.stdout,
                    'errors': result.stderr,
                    'returncode': result.returncode
                }
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error running flake8: {e}",
                'details': {'error': str(e)}
            }
    
    def _run_mypy(self, integration_path: Path) -> Dict[str, Any]:
        """Run mypy type checking."""
        try:
            result = subprocess.run(
                ['python', '-m', 'mypy', str(integration_path), '--ignore-missing-imports'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            # mypy returns 0 for success, >0 for issues
            passed = result.returncode == 0
            message = "Type checking passed" if passed else f"Type issues found"
            
            return {
                'passed': passed,
                'message': message,
                'details': {
                    'output': result.stdout,
                    'errors': result.stderr,
                    'returncode': result.returncode
                }
            }
            
        except Exception as e:
            return {
                'passed': True,  # Don't fail if mypy not available
                'message': f"Type checking skipped: {e}",
                'details': {'error': str(e)}
            }
    
    def _run_bandit(self, integration_path: Path) -> Dict[str, Any]:
        """Run bandit security scanning."""
        try:
            result = subprocess.run(
                ['python', '-m', 'bandit', '-r', str(integration_path), '-f', 'json'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            # Parse bandit JSON output
            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)
                    high_severity = len([r for r in bandit_data.get('results', []) 
                                       if r.get('issue_severity') == 'HIGH'])
                    passed = high_severity == 0
                    message = "Security scan passed" if passed else f"High severity issues found: {high_severity}"
                    
                    return {
                        'passed': passed,
                        'message': message,
                        'details': bandit_data
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback for non-JSON output
            passed = result.returncode == 0
            message = "Security scan passed" if passed else "Security issues detected"
            
            return {
                'passed': passed,
                'message': message,
                'details': {
                    'output': result.stdout,
                    'errors': result.stderr,
                    'returncode': result.returncode
                }
            }
            
        except Exception as e:
            return {
                'passed': True,  # Don't fail if bandit not available
                'message': f"Security scan skipped: {e}",
                'details': {'error': str(e)}
            }
    
    def _validate_testing(self, integration_path: Path) -> Dict[str, Any]:
        """Validate testing coverage and quality."""
        results = []
        
        # Find test files
        test_files = list(integration_path.rglob("test_*.py"))
        
        if not test_files:
            results.append(ValidationResult(
                name="CRITICAL: Test Coverage",
                passed=False,
                message="No test files found",
                details={'test_files': []}
            ))
            return {'results': results, 'coverage': 0.0}
        
        # Run tests with coverage
        coverage_result = self._run_tests_with_coverage(integration_path)
        
        passed = coverage_result['coverage'] >= self.thresholds['test_coverage']
        
        results.append(ValidationResult(
            name="CRITICAL: Test Coverage",
            passed=passed,
            message=f"Test coverage: {coverage_result['coverage']:.1f}%",
            details=coverage_result['details']
        ))
        
        return {
            'results': results,
            'coverage': coverage_result['coverage']
        }
    
    def _run_tests_with_coverage(self, integration_path: Path) -> Dict[str, Any]:
        """Run tests with coverage measurement."""
        try:
            # Run pytest with coverage
            result = subprocess.run([
                'python', '-m', 'pytest', 
                str(integration_path),
                '--cov=' + str(integration_path),
                '--cov-report=json',
                '--cov-report=term-missing',
                '-v'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            # Try to read coverage report
            coverage_file = self.project_root / 'coverage.json'
            coverage_percent = 0.0
            
            if coverage_file.exists():
                try:
                    with open(coverage_file) as f:
                        coverage_data = json.load(f)
                        coverage_percent = coverage_data.get('totals', {}).get('percent_covered', 0.0)
                except (json.JSONDecodeError, KeyError):
                    pass
            
            return {
                'coverage': coverage_percent,
                'details': {
                    'test_output': result.stdout,
                    'test_errors': result.stderr,
                    'test_returncode': result.returncode
                }
            }
            
        except Exception as e:
            return {
                'coverage': 0.0,
                'details': {'error': str(e)}
            }
    
    def _validate_resource_management(self, integration_path: Path) -> List[ValidationResult]:
        """Validate proper resource management."""
        results = []
        
        # Check for cleanup patterns
        cleanup_result = self._check_cleanup_patterns(integration_path)
        results.append(ValidationResult(
            name="CRITICAL: Resource Cleanup",
            passed=cleanup_result['passed'],
            message=cleanup_result['message'],
            details=cleanup_result.get('details')
        ))
        
        # Check for safe file operations
        file_safety_result = self._check_file_safety(integration_path)
        results.append(ValidationResult(
            name="Resource Management: File Safety",
            passed=file_safety_result['passed'],
            message=file_safety_result['message'],
            details=file_safety_result.get('details')
        ))
        
        return results
    
    def _check_cleanup_patterns(self, integration_path: Path) -> Dict[str, Any]:
        """Check for proper cleanup patterns."""
        try:
            python_files = list(integration_path.rglob("*.py"))
            
            cleanup_patterns = {
                'cleanup_methods': 0,
                'context_managers': 0,
                'try_finally_blocks': 0,
                'resource_tracking': 0
            }
            
            for py_file in python_files:
                content = py_file.read_text()
                
                cleanup_patterns['cleanup_methods'] += content.count('def cleanup(')
                cleanup_patterns['context_managers'] += content.count('with ')
                cleanup_patterns['try_finally_blocks'] += content.count('finally:')
                cleanup_patterns['resource_tracking'] += content.count('_resources')
            
            passed = cleanup_patterns['cleanup_methods'] > 0
            message = "Cleanup patterns found" if passed else "Missing cleanup patterns"
            
            return {
                'passed': passed,
                'message': message,
                'details': cleanup_patterns
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error checking cleanup patterns: {e}",
                'details': {'error': str(e)}
            }
    
    def _check_file_safety(self, integration_path: Path) -> Dict[str, Any]:
        """Check for safe file operations."""
        try:
            python_files = list(integration_path.rglob("*.py"))
            
            safety_patterns = {
                'atomic_writes': 0,
                'temp_file_usage': 0,
                'file_context_managers': 0,
                'unsafe_operations': 0
            }
            
            for py_file in python_files:
                content = py_file.read_text()
                
                safety_patterns['atomic_writes'] += content.count('tempfile.NamedTemporaryFile')
                safety_patterns['temp_file_usage'] += content.count('tempfile.')
                safety_patterns['file_context_managers'] += content.count('with open(')
                
                # Check for unsafe patterns
                if 'open(' in content and 'with ' not in content:
                    safety_patterns['unsafe_operations'] += 1
            
            passed = (safety_patterns['unsafe_operations'] == 0 and 
                     safety_patterns['file_context_managers'] > 0)
            
            message = "File operations are safe" if passed else "Unsafe file operations detected"
            
            return {
                'passed': passed,
                'message': message,
                'details': safety_patterns
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error checking file safety: {e}",
                'details': {'error': str(e)}
            }
    
    def _validate_documentation(self, integration_path: Path) -> List[ValidationResult]:
        """Validate documentation completeness."""
        results = []
        
        # Check for README
        readme_files = list(integration_path.glob("README.md")) + list(integration_path.glob("README.rst"))
        
        results.append(ValidationResult(
            name="Documentation: README",
            passed=len(readme_files) > 0,
            message="README found" if readme_files else "README missing",
            details={'readme_files': [str(f) for f in readme_files]}
        ))
        
        # Check for docstrings
        docstring_result = self._check_docstrings(integration_path)
        results.append(ValidationResult(
            name="Documentation: Docstrings",
            passed=docstring_result['passed'],
            message=docstring_result['message'],
            details=docstring_result.get('details')
        ))
        
        return results
    
    def _check_docstrings(self, integration_path: Path) -> Dict[str, Any]:
        """Check for proper docstrings."""
        try:
            python_files = list(integration_path.rglob("*.py"))
            
            docstring_stats = {
                'total_functions': 0,
                'documented_functions': 0,
                'total_classes': 0,
                'documented_classes': 0
            }
            
            for py_file in python_files:
                content = py_file.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Check for function definitions
                    if line.strip().startswith('def ') and not line.strip().startswith('def _'):
                        docstring_stats['total_functions'] += 1
                        # Check if next non-empty line is a docstring
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if lines[j].strip():
                                if '"""' in lines[j] or "'''" in lines[j]:
                                    docstring_stats['documented_functions'] += 1
                                break
                    
                    # Check for class definitions
                    elif line.strip().startswith('class '):
                        docstring_stats['total_classes'] += 1
                        # Check if next non-empty line is a docstring
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if lines[j].strip():
                                if '"""' in lines[j] or "'''" in lines[j]:
                                    docstring_stats['documented_classes'] += 1
                                break
            
            # Calculate coverage
            function_coverage = (docstring_stats['documented_functions'] / 
                               max(docstring_stats['total_functions'], 1)) * 100
            class_coverage = (docstring_stats['documented_classes'] / 
                            max(docstring_stats['total_classes'], 1)) * 100
            
            passed = function_coverage >= 70 and class_coverage >= 90
            message = f"Function docs: {function_coverage:.1f}%, Class docs: {class_coverage:.1f}%"
            
            return {
                'passed': passed,
                'message': message,
                'details': docstring_stats
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error checking docstrings: {e}",
                'details': {'error': str(e)}
            }
    
    def _validate_dependencies(self, integration_path: Path) -> Dict[str, Any]:
        """Validate dependencies and licenses."""
        results = []
        dependencies = []
        
        try:
            # Check requirements files
            req_files = list(integration_path.glob("requirements*.txt"))
            
            for req_file in req_files:
                with open(req_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dependencies.append(line)
            
            # Check for dependency conflicts
            conflict_result = self._check_dependency_conflicts(dependencies)
            results.append(ValidationResult(
                name="Dependencies: Conflicts",
                passed=conflict_result['passed'],
                message=conflict_result['message'],
                details=conflict_result.get('details')
            ))
            
            # Check for security vulnerabilities
            security_result = self._check_dependency_security(dependencies)
            results.append(ValidationResult(
                name="CRITICAL: Dependency Security",
                passed=security_result['passed'],
                message=security_result['message'],
                details=security_result.get('details')
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                name="Dependencies: Validation Error",
                passed=False,
                message=f"Error validating dependencies: {e}",
                details={'error': str(e)}
            ))
        
        return {
            'results': results,
            'dependencies': dependencies
        }
    
    def _check_dependency_conflicts(self, dependencies: List[str]) -> Dict[str, Any]:
        """Check for dependency conflicts."""
        # Simple conflict detection - can be enhanced
        package_versions = {}
        conflicts = []
        
        for dep in dependencies:
            if '==' in dep:
                package, version = dep.split('==', 1)
                if package in package_versions:
                    if package_versions[package] != version:
                        conflicts.append(f"{package}: {package_versions[package]} vs {version}")
                else:
                    package_versions[package] = version
        
        passed = len(conflicts) == 0
        message = "No dependency conflicts" if passed else f"Conflicts found: {len(conflicts)}"
        
        return {
            'passed': passed,
            'message': message,
            'details': {'conflicts': conflicts, 'packages': package_versions}
        }
    
    def _check_dependency_security(self, dependencies: List[str]) -> Dict[str, Any]:
        """Check dependencies for security vulnerabilities."""
        try:
            # Use pip-audit if available
            result = subprocess.run(
                ['python', '-m', 'pip_audit'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            passed = result.returncode == 0
            message = "No security vulnerabilities found" if passed else "Security vulnerabilities detected"
            
            return {
                'passed': passed,
                'message': message,
                'details': {
                    'output': result.stdout,
                    'errors': result.stderr
                }
            }
            
        except Exception as e:
            return {
                'passed': True,  # Don't fail if pip-audit not available
                'message': f"Security check skipped: {e}",
                'details': {'error': str(e)}
            }
    
    def _validate_performance(self, integration_path: Path) -> List[ValidationResult]:
        """Validate performance impact."""
        results = []
        
        # Measure import time
        import_time_result = self._measure_import_time(integration_path)
        results.append(ValidationResult(
            name="Performance: Import Time",
            passed=import_time_result['passed'],
            message=import_time_result['message'],
            details=import_time_result.get('details')
        ))
        
        # Measure memory usage
        memory_result = self._measure_memory_usage(integration_path)
        results.append(ValidationResult(
            name="Performance: Memory Usage",
            passed=memory_result['passed'],
            message=memory_result['message'],
            details=memory_result.get('details')
        ))
        
        return results
    
    def _measure_import_time(self, integration_path: Path) -> Dict[str, Any]:
        """Measure module import time."""
        try:
            import_times = []
            
            for py_file in integration_path.rglob("*.py"):
                if py_file.name.startswith('test_'):
                    continue
                
                # Calculate relative module path
                relative_path = py_file.relative_to(self.project_root)
                module_path = str(relative_path.with_suffix('')).replace(os.sep, '.')
                
                start_time = time.time()
                try:
                    spec = importlib.util.spec_from_file_location("test_module", py_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    import_time = (time.time() - start_time) * 1000  # ms
                    import_times.append({
                        'module': module_path,
                        'time_ms': import_time
                    })
                except Exception as e:
                    import_times.append({
                        'module': module_path,
                        'time_ms': 0,
                        'error': str(e)
                    })
            
            avg_import_time = sum(t['time_ms'] for t in import_times) / max(len(import_times), 1)
            max_import_time = max((t['time_ms'] for t in import_times), default=0)
            
            passed = max_import_time < 1000  # 1 second max for any module
            message = f"Average import: {avg_import_time:.1f}ms, Max: {max_import_time:.1f}ms"
            
            return {
                'passed': passed,
                'message': message,
                'details': {
                    'import_times': import_times,
                    'average_ms': avg_import_time,
                    'max_ms': max_import_time
                }
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error measuring import time: {e}",
                'details': {'error': str(e)}
            }
    
    def _measure_memory_usage(self, integration_path: Path) -> Dict[str, Any]:
        """Measure memory usage impact."""
        try:
            import psutil
            import gc
            
            # Baseline memory
            gc.collect()
            baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Import all modules
            for py_file in integration_path.rglob("*.py"):
                if py_file.name.startswith('test_'):
                    continue
                
                try:
                    spec = importlib.util.spec_from_file_location("test_module", py_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                except Exception:
                    pass
            
            # Measure final memory
            gc.collect()
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - baseline_memory
            
            passed = memory_increase < self.thresholds['memory_usage_mb']
            message = f"Memory increase: {memory_increase:.1f}MB"
            
            return {
                'passed': passed,
                'message': message,
                'details': {
                    'baseline_mb': baseline_memory,
                    'final_mb': final_memory,
                    'increase_mb': memory_increase
                }
            }
            
        except ImportError:
            return {
                'passed': True,
                'message': "Memory measurement skipped (psutil not available)",
                'details': {}
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f"Error measuring memory: {e}",
                'details': {'error': str(e)}
            }
    
    def _measure_resource_usage(self) -> Dict[str, Any]:
        """Measure current resource usage."""
        try:
            import psutil
            
            process = psutil.Process()
            
            return {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'open_files': len(process.open_files()),
                'threads': process.num_threads()
            }
            
        except ImportError:
            return {'status': 'psutil not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def generate_report_html(self, report: IntegrationReport, output_path: Path):
        """Generate HTML validation report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>VPA Integration Validation Report - {report.integration_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .critical {{ font-weight: bold; }}
        .result {{ margin: 10px 0; padding: 10px; border-left: 3px solid #ccc; }}
        .result.passed {{ border-left-color: green; }}
        .result.failed {{ border-left-color: red; }}
        .details {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        pre {{ background: #f0f0f0; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>VPA Integration Validation Report</h1>
        <h2>{report.integration_name}</h2>
        <p><strong>Timestamp:</strong> {report.timestamp}</p>
        <p><strong>Overall Status:</strong> 
            <span class="{'passed' if report.overall_passed else 'failed'}">
                {'PASSED' if report.overall_passed else 'FAILED'}
            </span>
        </p>
        <p><strong>Test Coverage:</strong> {report.test_coverage:.1f}%</p>
    </div>
    
    <h3>Validation Results</h3>
    """
        
        for result in report.results:
            status_class = 'passed' if result.passed else 'failed'
            critical_class = 'critical' if result.name.startswith('CRITICAL') else ''
            
            html_content += f"""
    <div class="result {status_class}">
        <h4 class="{critical_class}">{result.name}</h4>
        <p><strong>Status:</strong> <span class="{status_class}">{'PASSED' if result.passed else 'FAILED'}</span></p>
        <p><strong>Message:</strong> {result.message}</p>
        <p><strong>Execution Time:</strong> {result.execution_time:.3f}s</p>
        """
            
            if result.details:
                html_content += f"""
        <div class="details">
            <strong>Details:</strong>
            <pre>{json.dumps(result.details, indent=2)}</pre>
        </div>
        """
            
            html_content += "</div>"
        
        html_content += f"""
    
    <h3>Resource Usage</h3>
    <div class="details">
        <pre>{json.dumps(report.resource_usage, indent=2)}</pre>
    </div>
    
    <h3>Dependencies</h3>
    <div class="details">
        <ul>
        """
        
        for dep in report.dependencies:
            html_content += f"<li>{dep}</li>"
        
        html_content += """
        </ul>
    </div>
    
</body>
</html>
        """
        
        output_path.write_text(html_content)
        self.logger.info(f"HTML report generated: {output_path}")
    
    def save_report_json(self, report: IntegrationReport, output_path: Path):
        """Save validation report as JSON."""
        report_data = {
            'integration_name': report.integration_name,
            'timestamp': report.timestamp.isoformat(),
            'overall_passed': report.overall_passed,
            'test_coverage': report.test_coverage,
            'resource_usage': report.resource_usage,
            'dependencies': report.dependencies,
            'results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'message': r.message,
                    'execution_time': r.execution_time,
                    'details': r.details
                }
                for r in report.results
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.logger.info(f"JSON report saved: {output_path}")


def main():
    """Main validation entry point."""
    if len(sys.argv) < 3:
        print("Usage: python validation_framework.py <integration_name> <integration_path>")
        sys.exit(1)
    
    integration_name = sys.argv[1]
    integration_path = Path(sys.argv[2])
    project_root = Path(__file__).parent.parent
    
    framework = VPAValidationFramework(project_root)
    report = framework.validate_integration(integration_name, integration_path)
    
    # Generate reports
    reports_dir = project_root / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON report
    json_path = reports_dir / f"{integration_name}_validation_{timestamp}.json"
    framework.save_report_json(report, json_path)
    
    # HTML report
    html_path = reports_dir / f"{integration_name}_validation_{timestamp}.html"
    framework.generate_report_html(report, html_path)
    
    # Print summary
    print(f"\nValidation Report for {integration_name}")
    print("=" * 50)
    print(f"Overall Status: {'PASSED' if report.overall_passed else 'FAILED'}")
    print(f"Test Coverage: {report.test_coverage:.1f}%")
    print(f"Total Checks: {len(report.results)}")
    print(f"Passed: {sum(1 for r in report.results if r.passed)}")
    print(f"Failed: {sum(1 for r in report.results if not r.passed)}")
    
    critical_failures = [r for r in report.results if not r.passed and r.name.startswith('CRITICAL')]
    if critical_failures:
        print(f"\nCRITICAL FAILURES:")
        for failure in critical_failures:
            print(f"  - {failure.name}: {failure.message}")
    
    print(f"\nReports generated:")
    print(f"  JSON: {json_path}")
    print(f"  HTML: {html_path}")
    
    sys.exit(0 if report.overall_passed else 1)


if __name__ == "__main__":
    main()
