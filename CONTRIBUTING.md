# Contributing to VPA

Thank you for your interest in contributing to the Virtual Personal Assistant (VPA) project! This document provides guidelines and information for contributors.

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, or identity.

### Expected Behavior
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community and project
- Show empathy towards other community members

### Unacceptable Behavior
- Harassment, trolling, or discriminatory language
- Personal attacks or political discussions
- Publishing private information without permission
- Any conduct that would be inappropriate in a professional setting

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Git knowledge
- Familiarity with virtual environments
- Understanding of testing frameworks (pytest)

### Development Setup
1. **Fork and Clone**
   ```bash
   git clone git@github.com:YourUsername/VPA.git
   cd VPA
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt  # When available
   pip install -e .  # Install in development mode
   ```

4. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### 1. Issue-Based Development
- Always create or find an existing issue before starting work
- Comment on the issue to indicate you're working on it
- Reference the issue in your branch name: `feature/issue-123-add-voice-support`

### 2. Branch Naming Conventions
- **Features**: `feature/issue-number-brief-description`
- **Bug Fixes**: `bugfix/issue-number-brief-description`
- **Documentation**: `docs/issue-number-brief-description`
- **Refactoring**: `refactor/issue-number-brief-description`

### 3. Commit Message Format
```
type(scope): brief description

Detailed explanation of what changed and why.

- List specific changes
- Reference issues: Fixes #123, Relates to #456
- Breaking changes should be noted
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(nlp): add intent recognition for calendar commands

Implements basic intent classification for calendar-related
user inputs including creating, updating, and querying events.

- Add CalendarIntentClassifier class
- Integrate with existing NLP pipeline
- Add comprehensive test coverage
- Update documentation

Fixes #45
```

## Code Quality Standards

### 1. Code Style
- **Formatter**: Use Black with 88-character line length
- **Linter**: Use flake8 with project configuration
- **Import Sorting**: Use isort for consistent import organization
- **Type Checking**: Use mypy for static type checking

### 2. Pre-commit Checks
All code must pass these automated checks:
```bash
# Run before committing
black .                    # Code formatting
isort .                    # Import sorting
flake8 .                   # Linting
mypy src/                  # Type checking
pytest tests/              # Test suite
```

### 3. Testing Requirements

#### Test Coverage
- **Minimum**: 90% overall code coverage
- **New Features**: 100% coverage for new code
- **Critical Paths**: 100% coverage for security-related code

#### Test Types
```python
# Unit Test Example
def test_process_user_input_valid_command():
    """Test that valid commands are processed correctly."""
    assistant = VirtualAssistant()
    result = assistant.process("What's the weather today?")
    
    assert result.intent == "weather_query"
    assert result.confidence > 0.8
    assert "weather" in result.response.lower()

# Integration Test Example
def test_calendar_plugin_integration():
    """Test calendar plugin integration with core system."""
    assistant = VirtualAssistant()
    assistant.load_plugin("calendar")
    
    result = assistant.process("Schedule meeting tomorrow at 2pm")
    
    assert result.success
    assert "scheduled" in result.response.lower()
```

### 4. Documentation Requirements

#### Code Documentation
```python
class VirtualAssistant:
    """
    Main VPA class that orchestrates all assistant functionality.
    
    The VirtualAssistant class serves as the primary interface for
    processing user inputs and coordinating responses across all
    loaded plugins and services.
    
    Attributes:
        plugins: Dict of loaded plugins indexed by name
        config: System configuration object
        
    Example:
        >>> assistant = VirtualAssistant()
        >>> assistant.load_plugin("calendar")
        >>> response = assistant.process("What's on my schedule?")
        >>> print(response.content)
    """
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Response:
        """
        Process user input and generate appropriate response.
        
        Args:
            user_input: The user's natural language input
            context: Optional context from previous interactions
            
        Returns:
            Response object containing the assistant's reply and metadata
            
        Raises:
            ValidationError: If input validation fails
            ProcessingError: If response generation fails
        """
        pass
```

## Pull Request Process

### 1. Before Submitting
- [ ] Code follows style guidelines (Black, flake8, isort)
- [ ] All tests pass locally
- [ ] Code coverage meets minimum requirements
- [ ] Documentation is updated for new features
- [ ] CHANGELOG.md is updated (if applicable)

### 2. Pull Request Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Documentation
- [ ] Code comments updated
- [ ] README updated (if needed)
- [ ] API documentation updated (if needed)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests pass locally
- [ ] Documentation updated

Fixes #(issue number)
```

### 3. Review Process
1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer approval required
3. **Testing**: Reviewer will test functionality if applicable
4. **Documentation**: Ensure documentation is clear and complete

## Security Guidelines

### 1. Security-First Development
- Never commit secrets, API keys, or credentials
- Validate all user inputs using zero-trust principles
- Use parameterized queries for database operations
- Implement proper authentication and authorization

### 2. Dependency Management
- Regularly update dependencies for security patches
- Use `pip-audit` to check for known vulnerabilities
- Pin dependency versions in production requirements

### 3. Reporting Security Issues
- **DO NOT** create public issues for security vulnerabilities
- Email security concerns to: [security@vpa-project.com]
- Use GPG encryption for sensitive communications

## Community Guidelines

### 1. Communication Channels
- **GitHub Issues**: Bug reports, feature requests, general discussion
- **GitHub Discussions**: Questions, ideas, and community chat
- **Pull Requests**: Code review and technical discussion

### 2. Getting Help
- Check existing issues and documentation first
- Provide detailed information when asking questions
- Use appropriate labels and templates
- Be patient and respectful when waiting for responses

### 3. Recognition
Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- Project documentation for major features

## Release Process

### 1. Versioning
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### 2. Release Schedule
- **Major Releases**: Quarterly
- **Minor Releases**: Monthly
- **Patch Releases**: As needed for critical fixes

### 3. Contribution Recognition
- All contributors are acknowledged in release notes
- Significant contributions are highlighted
- First-time contributors are specially welcomed

## Questions and Support

### FAQ

**Q: How do I set up my development environment?**
A: Follow the "Getting Started" section above and ensure all pre-commit hooks are installed.

**Q: What if my tests are failing?**
A: Run tests locally first, check the test output for specific failures, and ensure your code follows the project standards.

**Q: How do I add a new plugin?**
A: Review the plugin architecture in `docs/SYSTEM_RULES.md` and look at existing plugins for examples.

**Q: Can I work on any open issue?**
A: Yes, but comment on the issue first to avoid duplicate work. Some issues may be reserved for specific contributors.

### Contact
- **General Questions**: Create a GitHub Discussion
- **Bug Reports**: Create a GitHub Issue
- **Security Issues**: Email [security@vpa-project.com]
- **Maintainers**: See `MAINTAINERS.md` for contact information

---

Thank you for contributing to VPA! Your efforts help make this project better for everyone.
