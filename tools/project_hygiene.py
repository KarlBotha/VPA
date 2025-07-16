#!/usr/bin/env python3
"""
VPA Project Hygiene Tool

Maintains code quality, structure, and best practices for VPA project.
"""

import os
import sys
import argparse
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import logging
import re
import ast


class VPAProjectHygiene:
    """Maintains VPA project hygiene and code quality."""
    
    def __init__(self, project_root: Path):
        """Initialize project hygiene manager."""
        self.project_root = project_root
        self.setup_logging()
        
        # Project structure
        self.src_dir = project_root / 'src'
        self.tests_dir = project_root / 'tests'
        self.docs_dir = project_root / 'docs'
        self.config_dir = project_root / 'config'
        self.tools_dir = project_root / 'tools'
        
        # Quality thresholds
        self.quality_thresholds = {
            'complexity': 10,
            'test_coverage': 80.0,
            'documentation_coverage': 70.0,
            'code_duplication': 5.0,
            'file_size_limit': 500  # lines
        }
        
        # File patterns
        self.python_files = ['*.py']
        self.test_files = ['test_*.py', '*_test.py']
        self.config_files = ['*.yaml', '*.yml', '*.json', '*.toml']
        self.doc_files = ['*.md', '*.rst', '*.txt']
        
    def setup_logging(self):
        """Setup logging for hygiene manager."""
        log_dir = self.project_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'hygiene_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_full_check(self) -> Dict[str, Any]:
        """Run comprehensive project hygiene check."""
        self.logger.info("Running full project hygiene check")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'checks': {}
        }
        
        # Structure check
        results['checks']['structure'] = self.check_project_structure()
        
        # Code quality
        results['checks']['code_quality'] = self.check_code_quality()
        
        # Documentation
        results['checks']['documentation'] = self.check_documentation()
        
        # Dependencies
        results['checks']['dependencies'] = self.check_dependencies()
        
        # Security
        results['checks']['security'] = self.check_security()
        
        # Performance
        results['checks']['performance'] = self.check_performance_patterns()
        
        # Calculate overall score
        results['overall_score'] = self._calculate_overall_score(results['checks'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results['checks'])
        
        self.logger.info(f"Hygiene check completed with score: {results['overall_score']:.2f}/100")
        
        return results
    
    def check_project_structure(self) -> Dict[str, Any]:
        """Check project structure compliance."""
        self.logger.info("Checking project structure")
        
        result = {
            'score': 0,
            'max_score': 100,
            'issues': [],
            'details': {}
        }
        
        # Expected directories
        expected_dirs = [
            'src/vpa',
            'src/vpa/core',
            'src/vpa/plugins',
            'tests',
            'docs',
            'config',
            'tools'
        ]
        
        missing_dirs = []
        for dir_path in expected_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        result['details']['missing_directories'] = missing_dirs
        
        # Expected files
        expected_files = [
            'README.md',
            'requirements.txt',
            'setup.py',
            '.gitignore',
            'src/vpa/__init__.py',
            'src/vpa/core/__init__.py'
        ]
        
        missing_files = []
        for file_path in expected_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        result['details']['missing_files'] = missing_files
        
        # Check for unwanted files
        unwanted_patterns = [
            '**/__pycache__',
            '**/*.pyc',
            '**/*.pyo',
            '**/.DS_Store',
            '**/Thumbs.db',
            '**/*.log'
        ]
        
        unwanted_files = []
        for pattern in unwanted_patterns:
            matches = list(self.project_root.glob(pattern))
            unwanted_files.extend([str(f.relative_to(self.project_root)) for f in matches])
        
        result['details']['unwanted_files'] = unwanted_files
        
        # Calculate score
        total_checks = len(expected_dirs) + len(expected_files)
        passed_checks = total_checks - len(missing_dirs) - len(missing_files)
        
        if unwanted_files:
            result['issues'].append(f"Found {len(unwanted_files)} unwanted files")
        
        if missing_dirs:
            result['issues'].extend([f"Missing directory: {d}" for d in missing_dirs])
        
        if missing_files:
            result['issues'].extend([f"Missing file: {f}" for f in missing_files])
        
        result['score'] = max(0, (passed_checks / total_checks) * 100 - len(unwanted_files) * 5)
        
        return result
    
    def check_code_quality(self) -> Dict[str, Any]:
        """Check code quality metrics."""
        self.logger.info("Checking code quality")
        
        result = {
            'score': 0,
            'max_score': 100,
            'issues': [],
            'details': {}
        }
        
        python_files = self._find_python_files()
        
        if not python_files:
            result['issues'].append("No Python files found")
            return result
        
        # Check complexity
        complexity_issues = self._check_complexity(python_files)
        result['details']['complexity'] = complexity_issues
        
        # Check style compliance
        style_issues = self._check_style(python_files)
        result['details']['style'] = style_issues
        
        # Check imports
        import_issues = self._check_imports(python_files)
        result['details']['imports'] = import_issues
        
        # Check docstrings
        docstring_issues = self._check_docstrings(python_files)
        result['details']['docstrings'] = docstring_issues
        
        # Check file sizes
        size_issues = self._check_file_sizes(python_files)
        result['details']['file_sizes'] = size_issues
        
        # Calculate score
        total_issues = (len(complexity_issues) + len(style_issues) + 
                       len(import_issues) + len(docstring_issues) + len(size_issues))
        
        if total_issues == 0:
            result['score'] = 100
        else:
            # Penalize based on issue count and severity
            penalty = min(total_issues * 5, 100)
            result['score'] = max(0, 100 - penalty)
        
        # Add issues to summary
        if complexity_issues:
            result['issues'].append(f"{len(complexity_issues)} complexity violations")
        if style_issues:
            result['issues'].append(f"{len(style_issues)} style violations")
        if import_issues:
            result['issues'].append(f"{len(import_issues)} import issues")
        if docstring_issues:
            result['issues'].append(f"{len(docstring_issues)} missing docstrings")
        if size_issues:
            result['issues'].append(f"{len(size_issues)} oversized files")
        
        return result
    
    def check_documentation(self) -> Dict[str, Any]:
        """Check documentation coverage and quality."""
        self.logger.info("Checking documentation")
        
        result = {
            'score': 0,
            'max_score': 100,
            'issues': [],
            'details': {}
        }
        
        # Check README
        readme_score = self._check_readme()
        result['details']['readme'] = readme_score
        
        # Check API documentation
        api_docs_score = self._check_api_docs()
        result['details']['api_docs'] = api_docs_score
        
        # Check inline documentation
        inline_docs_score = self._check_inline_docs()
        result['details']['inline_docs'] = inline_docs_score
        
        # Check documentation structure
        docs_structure_score = self._check_docs_structure()
        result['details']['docs_structure'] = docs_structure_score
        
        # Calculate overall score
        scores = [readme_score, api_docs_score, inline_docs_score, docs_structure_score]
        result['score'] = sum(scores) / len(scores)
        
        # Generate issues
        if readme_score < 80:
            result['issues'].append("README needs improvement")
        if api_docs_score < 70:
            result['issues'].append("API documentation insufficient")
        if inline_docs_score < 70:
            result['issues'].append("Inline documentation insufficient")
        if docs_structure_score < 80:
            result['issues'].append("Documentation structure needs improvement")
        
        return result
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check dependency management."""
        self.logger.info("Checking dependencies")
        
        result = {
            'score': 0,
            'max_score': 100,
            'issues': [],
            'details': {}
        }
        
        # Check requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if not req_file.exists():
            result['issues'].append("requirements.txt missing")
            result['score'] = 0
            return result
        
        # Parse requirements
        try:
            requirements = req_file.read_text().strip().split('\\n')
            requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]
            
            result['details']['total_dependencies'] = len(requirements)
            
            # Check for version pinning
            pinned = sum(1 for req in requirements if '==' in req or '>=' in req or '<=' in req)
            result['details']['pinned_dependencies'] = pinned
            result['details']['pinned_percentage'] = (pinned / len(requirements)) * 100 if requirements else 0
            
            # Check for security vulnerabilities (basic check)
            vulnerable_packages = self._check_vulnerable_packages(requirements)
            result['details']['vulnerable_packages'] = vulnerable_packages
            
            # Check for unused dependencies
            unused_deps = self._check_unused_dependencies(requirements)
            result['details']['unused_dependencies'] = unused_deps
            
            # Calculate score
            score = 100
            
            if result['details']['pinned_percentage'] < 80:
                score -= 20
                result['issues'].append("Many dependencies not version-pinned")
            
            if vulnerable_packages:
                score -= len(vulnerable_packages) * 15
                result['issues'].append(f"{len(vulnerable_packages)} potentially vulnerable packages")
            
            if unused_deps:
                score -= len(unused_deps) * 5
                result['issues'].append(f"{len(unused_deps)} potentially unused dependencies")
            
            result['score'] = max(0, score)
            
        except Exception as e:
            result['issues'].append(f"Error parsing requirements.txt: {e}")
            result['score'] = 20
        
        return result
    
    def check_security(self) -> Dict[str, Any]:
        """Check for security issues."""
        self.logger.info("Checking security")
        
        result = {
            'score': 0,
            'max_score': 100,
            'issues': [],
            'details': {}
        }
        
        # Check for hardcoded secrets
        secret_issues = self._check_hardcoded_secrets()
        result['details']['hardcoded_secrets'] = secret_issues
        
        # Check for unsafe patterns
        unsafe_patterns = self._check_unsafe_patterns()
        result['details']['unsafe_patterns'] = unsafe_patterns
        
        # Check file permissions (if applicable)
        permission_issues = self._check_file_permissions()
        result['details']['file_permissions'] = permission_issues
        
        # Check for .env and secrets handling
        env_handling = self._check_env_handling()
        result['details']['env_handling'] = env_handling
        
        # Calculate score
        total_issues = len(secret_issues) + len(unsafe_patterns) + len(permission_issues)
        
        if total_issues == 0 and env_handling['score'] > 80:
            result['score'] = 100
        else:
            penalty = total_issues * 20 + (100 - env_handling['score']) * 0.2
            result['score'] = max(0, 100 - penalty)
        
        # Generate issues
        if secret_issues:
            result['issues'].append(f"{len(secret_issues)} potential hardcoded secrets")
        if unsafe_patterns:
            result['issues'].append(f"{len(unsafe_patterns)} unsafe code patterns")
        if permission_issues:
            result['issues'].append(f"{len(permission_issues)} file permission issues")
        if env_handling['score'] < 80:
            result['issues'].append("Environment/secrets handling needs improvement")
        
        return result
    
    def check_performance_patterns(self) -> Dict[str, Any]:
        """Check for performance anti-patterns."""
        self.logger.info("Checking performance patterns")
        
        result = {
            'score': 0,
            'max_score': 100,
            'issues': [],
            'details': {}
        }
        
        python_files = self._find_python_files()
        
        # Check for common anti-patterns
        antipatterns = self._check_performance_antipatterns(python_files)
        result['details']['antipatterns'] = antipatterns
        
        # Check for inefficient loops
        loop_issues = self._check_inefficient_loops(python_files)
        result['details']['loop_issues'] = loop_issues
        
        # Check for memory leaks patterns
        memory_issues = self._check_memory_patterns(python_files)
        result['details']['memory_issues'] = memory_issues
        
        # Calculate score
        total_issues = len(antipatterns) + len(loop_issues) + len(memory_issues)
        
        if total_issues == 0:
            result['score'] = 100
        else:
            penalty = min(total_issues * 10, 100)
            result['score'] = max(0, 100 - penalty)
        
        # Generate issues
        if antipatterns:
            result['issues'].append(f"{len(antipatterns)} performance anti-patterns")
        if loop_issues:
            result['issues'].append(f"{len(loop_issues)} inefficient loops")
        if memory_issues:
            result['issues'].append(f"{len(memory_issues)} potential memory issues")
        
        return result
    
    def fix_common_issues(self, issues_to_fix: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fix common project hygiene issues."""
        self.logger.info("Fixing common hygiene issues")
        
        result = {
            'fixed': [],
            'failed': [],
            'skipped': []
        }
        
        available_fixes = {
            'remove_unwanted_files': self._fix_unwanted_files,
            'format_code': self._fix_code_formatting,
            'fix_imports': self._fix_import_order,
            'update_gitignore': self._fix_gitignore,
            'create_missing_files': self._fix_missing_files
        }
        
        fixes_to_apply = issues_to_fix or list(available_fixes.keys())
        
        for fix_name in fixes_to_apply:
            if fix_name in available_fixes:
                try:
                    self.logger.info(f"Applying fix: {fix_name}")
                    success = available_fixes[fix_name]()
                    
                    if success:
                        result['fixed'].append(fix_name)
                        self.logger.info(f"Successfully applied fix: {fix_name}")
                    else:
                        result['failed'].append(fix_name)
                        self.logger.warning(f"Failed to apply fix: {fix_name}")
                        
                except Exception as e:
                    result['failed'].append(fix_name)
                    self.logger.error(f"Error applying fix {fix_name}: {e}")
            else:
                result['skipped'].append(fix_name)
        
        return result
    
    def generate_report(self, results: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
        """Generate detailed hygiene report."""
        if output_path is None:
            output_path = self.project_root / 'reports' / f'hygiene_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = self._generate_html_report(results)
        output_path.write_text(html_content)
        
        self.logger.info(f"Hygiene report generated: {output_path}")
        return output_path
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        
        for pattern in self.python_files:
            python_files.extend(self.src_dir.glob(f"**/{pattern}"))
            python_files.extend(self.tests_dir.glob(f"**/{pattern}") if self.tests_dir.exists() else [])
        
        return [f for f in python_files if f.is_file()]
    
    def _check_complexity(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Check code complexity."""
        issues = []
        
        for file_path in files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = self._calculate_complexity(node)
                        if complexity > self.quality_thresholds['complexity']:
                            issues.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'function': node.name,
                                'line': node.lineno,
                                'complexity': complexity,
                                'threshold': self.quality_thresholds['complexity']
                            })
            except Exception as e:
                self.logger.warning(f"Error analyzing complexity in {file_path}: {e}")
        
        return issues
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _check_style(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Check code style compliance."""
        issues = []
        
        # Use flake8 if available
        try:
            for file_path in files:
                result = subprocess.run([
                    'flake8', '--max-line-length=88', '--ignore=E203,W503', str(file_path)
                ], capture_output=True, text=True)
                
                if result.stdout:
                    for line in result.stdout.strip().split('\\n'):
                        if line:
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                issues.append({
                                    'file': str(file_path.relative_to(self.project_root)),
                                    'line': int(parts[1]),
                                    'column': int(parts[2]),
                                    'message': parts[3].strip()
                                })
        except FileNotFoundError:
            self.logger.warning("flake8 not available for style checking")
        
        return issues
    
    def _check_imports(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Check import organization."""
        issues = []
        
        for file_path in files:
            try:
                content = file_path.read_text()
                lines = content.split('\\n')
                
                # Check for unused imports (basic check)
                imports = []
                for i, line in enumerate(lines):
                    if line.strip().startswith(('import ', 'from ')):
                        imports.append((i + 1, line.strip()))
                
                # Simple check for import order
                if len(imports) > 1:
                    stdlib_imports = []
                    third_party_imports = []
                    local_imports = []
                    
                    for line_num, import_line in imports:
                        if 'from .' in import_line or 'from vpa' in import_line:
                            local_imports.append((line_num, import_line))
                        elif any(lib in import_line for lib in ['os', 'sys', 'json', 'datetime', 'typing']):
                            stdlib_imports.append((line_num, import_line))
                        else:
                            third_party_imports.append((line_num, import_line))
                    
                    # Check if imports are properly grouped
                    all_imports = stdlib_imports + third_party_imports + local_imports
                    current_order = [item[0] for item in imports]
                    expected_order = [item[0] for item in all_imports]
                    
                    if current_order != expected_order:
                        issues.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'issue': 'Import order not following PEP 8',
                            'line': imports[0][0]
                        })
                        
            except Exception as e:
                self.logger.warning(f"Error checking imports in {file_path}: {e}")
        
        return issues
    
    def _check_docstrings(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Check for missing docstrings."""
        issues = []
        
        for file_path in files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        # Skip private methods and test methods
                        if node.name.startswith('_') or node.name.startswith('test_'):
                            continue
                        
                        # Check if docstring exists
                        has_docstring = (ast.get_docstring(node) is not None)
                        
                        if not has_docstring:
                            issues.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'name': node.name,
                                'type': type(node).__name__,
                                'line': node.lineno
                            })
                            
            except Exception as e:
                self.logger.warning(f"Error checking docstrings in {file_path}: {e}")
        
        return issues
    
    def _check_file_sizes(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Check for oversized files."""
        issues = []
        
        for file_path in files:
            try:
                content = file_path.read_text()
                line_count = len(content.split('\\n'))
                
                if line_count > self.quality_thresholds['file_size_limit']:
                    issues.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'lines': line_count,
                        'limit': self.quality_thresholds['file_size_limit']
                    })
                    
            except Exception as e:
                self.logger.warning(f"Error checking file size {file_path}: {e}")
        
        return issues
    
    def _check_readme(self) -> float:
        """Check README quality."""
        readme_path = self.project_root / 'README.md'
        
        if not readme_path.exists():
            return 0
        
        try:
            content = readme_path.read_text().lower()
            
            # Check for essential sections
            sections = ['installation', 'usage', 'configuration', 'contributing', 'license']
            section_score = sum(1 for section in sections if section in content) / len(sections)
            
            # Check for code examples
            has_code = '```' in content or '`' in content
            
            # Check length
            words = len(content.split())
            length_score = min(words / 500, 1.0)  # Expect at least 500 words
            
            # Calculate overall score
            score = (section_score * 0.5 + (1 if has_code else 0) * 0.3 + length_score * 0.2) * 100
            
            return score
            
        except Exception as e:
            self.logger.warning(f"Error checking README: {e}")
            return 0
    
    def _check_api_docs(self) -> float:
        """Check API documentation."""
        docs_dir = self.docs_dir / 'api'
        
        if not docs_dir.exists():
            return 0
        
        # Count documented modules
        python_files = self._find_python_files()
        doc_files = list(docs_dir.glob('*.md'))
        
        if not python_files:
            return 100
        
        # Simple heuristic: expect at least one doc file per 5 Python files
        expected_docs = max(1, len(python_files) // 5)
        coverage = min(len(doc_files) / expected_docs, 1.0)
        
        return coverage * 100
    
    def _check_inline_docs(self) -> float:
        """Check inline documentation coverage."""
        python_files = self._find_python_files()
        
        if not python_files:
            return 100
        
        total_functions = 0
        documented_functions = 0
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not node.name.startswith('_'):  # Skip private methods
                            total_functions += 1
                            if ast.get_docstring(node):
                                documented_functions += 1
                                
            except Exception as e:
                self.logger.warning(f"Error checking inline docs in {file_path}: {e}")
        
        if total_functions == 0:
            return 100
        
        coverage = (documented_functions / total_functions) * 100
        return coverage
    
    def _check_docs_structure(self) -> float:
        """Check documentation structure."""
        if not self.docs_dir.exists():
            return 0
        
        expected_files = ['README.md', 'CONTRIBUTING.md', 'CHANGELOG.md']
        existing_files = sum(1 for f in expected_files if (self.project_root / f).exists())
        
        expected_dirs = ['api', 'guides', 'examples']
        existing_dirs = sum(1 for d in expected_dirs if (self.docs_dir / d).exists())
        
        structure_score = (existing_files / len(expected_files) + existing_dirs / len(expected_dirs)) / 2
        
        return structure_score * 100
    
    def _check_vulnerable_packages(self, requirements: List[str]) -> List[str]:
        """Check for known vulnerable packages."""
        # Simple list of commonly vulnerable packages
        # In production, this would integrate with safety or similar tools
        vulnerable_patterns = ['pillow<8.0.0', 'django<2.2', 'flask<1.0']
        
        vulnerable = []
        for req in requirements:
            for pattern in vulnerable_patterns:
                if any(vuln in req.lower() for vuln in ['pillow', 'django', 'flask']):
                    vulnerable.append(req)
                    break
        
        return vulnerable
    
    def _check_unused_dependencies(self, requirements: List[str]) -> List[str]:
        """Check for potentially unused dependencies."""
        # This is a simplified check - in practice would analyze imports
        python_files = self._find_python_files()
        
        if not python_files:
            return []
        
        # Get all imports from code
        used_packages = set()
        for file_path in python_files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            used_packages.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            used_packages.add(node.module.split('.')[0])
                            
            except Exception:
                continue
        
        # Check which requirements might be unused
        unused = []
        for req in requirements:
            package_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
            package_name = package_name.replace('-', '_').replace('.', '_').lower()
            
            if package_name not in used_packages:
                # Some packages have different import names
                common_mappings = {
                    'pyyaml': 'yaml',
                    'pillow': 'PIL',
                    'beautifulsoup4': 'bs4'
                }
                
                import_name = common_mappings.get(package_name, package_name)
                if import_name not in used_packages:
                    unused.append(req)
        
        return unused
    
    def _check_hardcoded_secrets(self) -> List[Dict[str, Any]]:
        """Check for hardcoded secrets."""
        issues = []
        
        # Patterns that might indicate secrets
        secret_patterns = [
            r'password\\s*=\\s*["\'][^"\']+["\']',
            r'api_key\\s*=\\s*["\'][^"\']+["\']',
            r'secret\\s*=\\s*["\'][^"\']+["\']',
            r'token\\s*=\\s*["\'][^"\']+["\']',
            r'["\'][A-Za-z0-9]{20,}["\']'  # Long strings that might be keys
        ]
        
        all_files = list(self.project_root.glob('**/*.py'))
        all_files.extend(self.project_root.glob('**/*.yaml'))
        all_files.extend(self.project_root.glob('**/*.yml'))
        all_files.extend(self.project_root.glob('**/*.json'))
        
        for file_path in all_files:
            if '.git' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                content = file_path.read_text()
                
                for i, line in enumerate(content.split('\\n'), 1):
                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip obvious test values
                            if any(test_val in line.lower() for test_val in ['test', 'example', 'dummy', 'fake']):
                                continue
                                
                            issues.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'content': line.strip()[:100] + ('...' if len(line.strip()) > 100 else '')
                            })
                            
            except Exception as e:
                self.logger.warning(f"Error checking secrets in {file_path}: {e}")
        
        return issues
    
    def _check_unsafe_patterns(self) -> List[Dict[str, Any]]:
        """Check for unsafe code patterns."""
        issues = []
        
        unsafe_patterns = [
            (r'eval\\s*\\(', 'Use of eval()'),
            (r'exec\\s*\\(', 'Use of exec()'),
            (r'subprocess\\.call\\s*\\([^)]*shell\\s*=\\s*True', 'subprocess with shell=True'),
            (r'os\\.system\\s*\\(', 'Use of os.system()'),
            (r'pickle\\.loads\\s*\\(', 'Unsafe pickle.loads()'),
            (r'yaml\\.load\\s*\\([^)]*\\)', 'Unsafe yaml.load() - use safe_load()')
        ]
        
        python_files = self._find_python_files()
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                for i, line in enumerate(content.split('\\n'), 1):
                    for pattern, description in unsafe_patterns:
                        if re.search(pattern, line):
                            issues.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'pattern': description,
                                'content': line.strip()
                            })
                            
            except Exception as e:
                self.logger.warning(f"Error checking unsafe patterns in {file_path}: {e}")
        
        return issues
    
    def _check_file_permissions(self) -> List[Dict[str, Any]]:
        """Check file permissions."""
        issues = []
        
        # Check for overly permissive files
        sensitive_files = [
            'config/*.yaml',
            'config/*.yml', 
            'secrets/*',
            '.env*',
            '*.pem',
            '*.key'
        ]
        
        for pattern in sensitive_files:
            for file_path in self.project_root.glob(pattern):
                try:
                    if file_path.is_file():
                        # On Windows, permission checking is limited
                        # This is a placeholder for Unix-like systems
                        stat_info = file_path.stat()
                        
                        # Check if file is world-readable (simplified check)
                        if hasattr(stat_info, 'st_mode'):
                            mode = stat_info.st_mode
                            if mode & 0o044:  # World/group readable
                                issues.append({
                                    'file': str(file_path.relative_to(self.project_root)),
                                    'issue': 'File may be too permissive',
                                    'mode': oct(mode)[-3:]
                                })
                                
                except Exception as e:
                    self.logger.warning(f"Error checking permissions for {file_path}: {e}")
        
        return issues
    
    def _check_env_handling(self) -> Dict[str, Any]:
        """Check environment and secrets handling."""
        result = {'score': 0, 'issues': []}
        
        # Check for .env.example
        env_example = self.project_root / '.env.example'
        has_env_example = env_example.exists()
        
        # Check .gitignore for env files
        gitignore = self.project_root / '.gitignore'
        gitignore_includes_env = False
        
        if gitignore.exists():
            content = gitignore.read_text()
            gitignore_includes_env = '.env' in content
        
        # Check for environment variable usage in code
        python_files = self._find_python_files()
        uses_env_vars = False
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                if 'os.environ' in content or 'getenv' in content:
                    uses_env_vars = True
                    break
            except Exception:
                continue
        
        # Calculate score
        score = 0
        if has_env_example:
            score += 40
        if gitignore_includes_env:
            score += 40
        if uses_env_vars:
            score += 20
        
        result['score'] = score
        
        if not has_env_example:
            result['issues'].append("Missing .env.example file")
        if not gitignore_includes_env:
            result['issues'].append(".gitignore doesn't exclude .env files")
        if not uses_env_vars:
            result['issues'].append("No environment variable usage detected")
        
        return result
    
    def _check_performance_antipatterns(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Check for performance anti-patterns."""
        issues = []
        
        antipatterns = [
            (r'\\+\\s*=.*in\\s+loop', 'String concatenation in loop'),
            (r'list\\(.*\\)\\s*\\+\\s*list\\(.*\\)', 'Inefficient list concatenation'),
            (r'len\\(.*\\)\\s*>\\s*0', 'Use "if container:" instead of "if len(container) > 0"'),
            (r'\\brange\\(len\\(.*\\)\\)', 'Use enumerate() instead of range(len())'),
        ]
        
        for file_path in files:
            try:
                content = file_path.read_text()
                
                for i, line in enumerate(content.split('\\n'), 1):
                    for pattern, description in antipatterns:
                        if re.search(pattern, line):
                            issues.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'pattern': description,
                                'content': line.strip()
                            })
                            
            except Exception as e:
                self.logger.warning(f"Error checking performance patterns in {file_path}: {e}")
        
        return issues
    
    def _check_inefficient_loops(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Check for inefficient loop patterns."""
        issues = []
        
        for file_path in files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.For):
                        # Check for nested loops
                        nested_loops = [n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While)) and n != node]
                        if len(nested_loops) >= 2:
                            issues.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': node.lineno,
                                'issue': f'Nested loops (depth: {len(nested_loops) + 1})',
                                'suggestion': 'Consider optimization or breaking into functions'
                            })
                            
            except Exception as e:
                self.logger.warning(f"Error checking loops in {file_path}: {e}")
        
        return issues
    
    def _check_memory_patterns(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Check for potential memory issues."""
        issues = []
        
        memory_patterns = [
            (r'\\*\\s*args', 'Potential memory issue with *args'),
            (r'\\*\\*\\s*kwargs', 'Potential memory issue with **kwargs'),
            (r'\\[.*for.*in.*\\]', 'List comprehension - consider generator for large data'),
        ]
        
        for file_path in files:
            try:
                content = file_path.read_text()
                
                for i, line in enumerate(content.split('\\n'), 1):
                    for pattern, description in memory_patterns:
                        if re.search(pattern, line) and 'large' in line.lower():
                            issues.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'pattern': description,
                                'content': line.strip()
                            })
                            
            except Exception as e:
                self.logger.warning(f"Error checking memory patterns in {file_path}: {e}")
        
        return issues
    
    def _calculate_overall_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall hygiene score."""
        weights = {
            'structure': 0.2,
            'code_quality': 0.25,
            'documentation': 0.15,
            'dependencies': 0.15,
            'security': 0.15,
            'performance': 0.1
        }
        
        total_score = 0
        total_weight = 0
        
        for check_name, weight in weights.items():
            if check_name in checks:
                score = checks[check_name]['score']
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def _generate_recommendations(self, checks: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Structure recommendations
        if checks.get('structure', {}).get('score', 0) < 80:
            recommendations.append("Improve project structure - ensure all expected directories and files exist")
        
        # Code quality recommendations
        if checks.get('code_quality', {}).get('score', 0) < 70:
            recommendations.append("Focus on code quality - reduce complexity, improve style, add docstrings")
        
        # Documentation recommendations
        if checks.get('documentation', {}).get('score', 0) < 70:
            recommendations.append("Enhance documentation - improve README, add API docs, increase inline documentation")
        
        # Security recommendations
        if checks.get('security', {}).get('score', 0) < 80:
            recommendations.append("Address security concerns - review hardcoded secrets, unsafe patterns, file permissions")
        
        # Performance recommendations
        if checks.get('performance', {}).get('score', 0) < 80:
            recommendations.append("Optimize performance - review anti-patterns, inefficient loops, memory usage")
        
        return recommendations
    
    def _fix_unwanted_files(self) -> bool:
        """Remove unwanted files."""
        try:
            unwanted_patterns = [
                '**/__pycache__',
                '**/*.pyc',
                '**/*.pyo',
                '**/.DS_Store',
                '**/Thumbs.db'
            ]
            
            removed_count = 0
            
            for pattern in unwanted_patterns:
                for path in self.project_root.glob(pattern):
                    if path.is_file():
                        path.unlink()
                        removed_count += 1
                    elif path.is_dir():
                        shutil.rmtree(path)
                        removed_count += 1
            
            self.logger.info(f"Removed {removed_count} unwanted files/directories")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing unwanted files: {e}")
            return False
    
    def _fix_code_formatting(self) -> bool:
        """Fix code formatting."""
        try:
            python_files = self._find_python_files()
            
            # Try to use black for formatting
            for file_path in python_files:
                result = subprocess.run([
                    'black', '--line-length', '88', str(file_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.logger.warning(f"Failed to format {file_path}: {result.stderr}")
            
            self.logger.info(f"Formatted {len(python_files)} Python files")
            return True
            
        except FileNotFoundError:
            self.logger.warning("black not available for code formatting")
            return False
        except Exception as e:
            self.logger.error(f"Error formatting code: {e}")
            return False
    
    def _fix_import_order(self) -> bool:
        """Fix import order."""
        try:
            python_files = self._find_python_files()
            
            # Try to use isort for import sorting
            for file_path in python_files:
                result = subprocess.run([
                    'isort', str(file_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.logger.warning(f"Failed to sort imports in {file_path}: {result.stderr}")
            
            self.logger.info(f"Sorted imports in {len(python_files)} Python files")
            return True
            
        except FileNotFoundError:
            self.logger.warning("isort not available for import sorting")
            return False
        except Exception as e:
            self.logger.error(f"Error sorting imports: {e}")
            return False
    
    def _fix_gitignore(self) -> bool:
        """Update .gitignore with standard patterns."""
        try:
            gitignore_path = self.project_root / '.gitignore'
            
            standard_patterns = """
# VPA Specific
logs/
temp/
cache/
*.log
config/local_*.yaml
secrets/
.env
data/conversations/
data/temp/
reports/
coverage.json
.coverage
.pytest_cache/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
            
            if gitignore_path.exists():
                content = gitignore_path.read_text()
                if "# VPA Specific" not in content:
                    content += standard_patterns
                    gitignore_path.write_text(content)
            else:
                gitignore_path.write_text(standard_patterns.strip())
            
            self.logger.info("Updated .gitignore")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating .gitignore: {e}")
            return False
    
    def _fix_missing_files(self) -> bool:
        """Create missing essential files."""
        try:
            # Create __init__.py files
            init_files = [
                'src/__init__.py',
                'src/vpa/__init__.py',
                'src/vpa/core/__init__.py',
                'src/vpa/plugins/__init__.py'
            ]
            
            for init_file in init_files:
                init_path = self.project_root / init_file
                if not init_path.exists():
                    init_path.parent.mkdir(parents=True, exist_ok=True)
                    init_path.write_text('"""VPA Package"""\\n')
            
            # Create basic setup.py if missing
            setup_path = self.project_root / 'setup.py'
            if not setup_path.exists():
                setup_content = '''"""Setup script for VPA."""

from setuptools import setup, find_packages

setup(
    name="vpa",
    version="0.1.0",
    description="Virtual Personal Assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Add your dependencies here
    ],
)
'''
                setup_path.write_text(setup_content)
            
            self.logger.info("Created missing essential files")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating missing files: {e}")
            return False
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate HTML report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>VPA Project Hygiene Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 24px; font-weight: bold; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .good {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
        .issues {{ margin: 10px 0; }}
        .issue {{ margin: 5px 0; padding: 5px; background: #f9f9f9; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .recommendations {{ background: #e6f3ff; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>VPA Project Hygiene Report</h1>
        <p>Generated: {results['timestamp']}</p>
        <p>Project: {results['project_root']}</p>
        <div class="score">Overall Score: {results['overall_score']:.1f}/100</div>
    </div>
"""
        
        # Checks summary
        html += "<h2>Check Results</h2>"
        html += "<table><tr><th>Check</th><th>Score</th><th>Issues</th></tr>"
        
        for check_name, check_data in results['checks'].items():
            score = check_data['score']
            issues_count = len(check_data['issues'])
            
            score_class = 'good' if score >= 80 else 'warning' if score >= 60 else 'error'
            
            html += f"""
            <tr>
                <td>{check_name.replace('_', ' ').title()}</td>
                <td class="{score_class}">{score:.1f}</td>
                <td>{issues_count}</td>
            </tr>
            """
        
        html += "</table>"
        
        # Detailed results
        for check_name, check_data in results['checks'].items():
            html += f"""
            <div class="section">
                <h3>{check_name.replace('_', ' ').title()}</h3>
                <p>Score: {check_data['score']:.1f}/{check_data['max_score']}</p>
                """
            
            if check_data['issues']:
                html += "<div class='issues'><h4>Issues:</h4>"
                for issue in check_data['issues']:
                    html += f"<div class='issue'>{issue}</div>"
                html += "</div>"
            
            html += "</div>"
        
        # Recommendations
        if results.get('recommendations'):
            html += """
            <div class="recommendations">
                <h3>Recommendations</h3>
                <ul>
            """
            
            for rec in results['recommendations']:
                html += f"<li>{rec}</li>"
            
            html += "</ul></div>"
        
        html += """
</body>
</html>
"""
        
        return html


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="VPA Project Hygiene Tool")
    
    parser.add_argument('--project-root', type=Path, default=Path.cwd(),
                       help='Project root directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Run hygiene check')
    check_parser.add_argument('--output', type=Path, help='Output report path')
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Fix common issues')
    fix_parser.add_argument('--issues', nargs='*', help='Specific issues to fix')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate detailed report')
    report_parser.add_argument('--output', type=Path, help='Output report path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    hygiene = VPAProjectHygiene(args.project_root)
    
    if args.command == 'check':
        results = hygiene.run_full_check()
        
        print(f"Project Hygiene Check Results")
        print(f"============================")
        print(f"Overall Score: {results['overall_score']:.1f}/100\\n")
        
        for check_name, check_data in results['checks'].items():
            print(f"{check_name.replace('_', ' ').title()}: {check_data['score']:.1f}/100")
            if check_data['issues']:
                for issue in check_data['issues']:
                    print(f"  - {issue}")
        
        if results.get('recommendations'):
            print("\\nRecommendations:")
            for rec in results['recommendations']:
                print(f"  - {rec}")
        
        if args.output:
            hygiene.generate_report(results, args.output)
            print(f"\\nDetailed report saved to: {args.output}")
    
    elif args.command == 'fix':
        fix_results = hygiene.fix_common_issues(args.issues)
        
        print("Fix Results:")
        print(f"Fixed: {len(fix_results['fixed'])} issues")
        print(f"Failed: {len(fix_results['failed'])} issues")
        print(f"Skipped: {len(fix_results['skipped'])} issues")
        
        if fix_results['fixed']:
            print("\\nFixed issues:")
            for issue in fix_results['fixed']:
                print(f"  - {issue}")
        
        if fix_results['failed']:
            print("\\nFailed to fix:")
            for issue in fix_results['failed']:
                print(f"  - {issue}")
    
    elif args.command == 'report':
        results = hygiene.run_full_check()
        output_path = hygiene.generate_report(results, args.output)
        print(f"Detailed report generated: {output_path}")


if __name__ == "__main__":
    main()
