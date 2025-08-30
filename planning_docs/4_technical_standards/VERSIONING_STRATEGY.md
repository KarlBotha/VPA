# Versioning Strategy

## Overview

This document outlines the version management strategy for the Virtual Personal Assistant (VPA) project. It defines the versioning scheme, release process, backward compatibility guidelines, and dependency management approach. The versioning strategy ensures consistency across all components, provides clear communication about changes, and supports reliable updates and rollbacks.

## Versioning Scheme

The VPA project follows [Semantic Versioning 2.0.0](https://semver.org/) (SemVer) for all components, libraries, APIs, and the overall application.

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

For example: `1.2.3-beta.1+20250829`

### Version Components

1. **MAJOR**: Incremented for incompatible API changes or significant architectural changes
   - Requires data migration and/or system configuration changes
   - May break backward compatibility with plugins or integrations
   - Example: Moving from synchronous to asynchronous core architecture

2. **MINOR**: Incremented for backward-compatible feature additions
   - New functionality without breaking existing features
   - Backward compatible with the same MAJOR version
   - Example: Adding a new plugin capability or voice model

3. **PATCH**: Incremented for backward-compatible bug fixes
   - No new functionality, only corrections to existing features
   - No API changes
   - Example: Fixing a memory leak or correcting a calculation error

4. **PRERELEASE** (optional): Indicates a pre-release version
   - Format: `-<identifier>.<number>`
   - Common identifiers: `alpha`, `beta`, `rc` (release candidate)
   - Example: `1.4.0-beta.2`

5. **BUILD** (optional): Build metadata
   - Format: `+<build-information>`
   - May include build date, commit hash, or CI job number
   - Example: `1.4.0+20250829-commit-a7d3b`

### Initial Development

Before reaching 1.0.0 (initial stable release):
- Use `0.y.z` format
- The API is considered unstable and may change without notice
- Each `0.y` increment represents a significant development milestone

## Version Control Strategy

### Branch Structure

The VPA project uses a modified GitFlow workflow with the following branches:

1. **main**: Represents the latest stable release
   - Always in a deployable state
   - Tagged with version numbers for releases
   - Protected branch requiring code review and CI passing

2. **develop**: Main development branch
   - Contains the latest merged features for the next release
   - Regular integration testing
   - Protected branch requiring code review

3. **feature/***:  Short-lived branches for new features
   - Branched from: `develop`
   - Merged back into: `develop`
   - Naming: `feature/brief-description-of-feature`
   - Example: `feature/multi-voice-support`

4. **release/***:  Preparation for a new release
   - Branched from: `develop`
   - Merged back into: `develop` and `main`
   - Only bug fixes, documentation, and release-oriented tasks
   - Naming: `release/x.y.z`
   - Example: `release/1.2.0`

5. **hotfix/***:  Urgent fixes for production issues
   - Branched from: `main`
   - Merged back into: `develop` and `main`
   - Naming: `hotfix/brief-description`
   - Example: `hotfix/critical-memory-leak`

### Commit Message Format

The project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: Code changes that neither fix a bug nor add a feature
- `perf`: Performance improvements
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes to the build system or external dependencies
- `ci`: Changes to CI configuration files and scripts

Examples:
```
feat(audio): add support for multiple voice profiles
fix(gui): prevent memory leak in notification manager
docs(api): update authentication documentation
```

## Release Process

### Release Types

1. **Major Release**:
   - Significant new functionality or breaking changes
   - Full regression testing and documentation updates
   - Planned and communicated well in advance
   - Typically every 6-12 months

2. **Minor Release**:
   - New features and non-breaking improvements
   - Regression testing for affected areas
   - Typically every 1-3 months

3. **Patch Release**:
   - Bug fixes and security updates
   - Minimal changes to reduce risk
   - As needed, typically every 2-4 weeks

4. **Hotfix Release**:
   - Critical bug fixes or security patches
   - Minimally invasive changes
   - Released as soon as verified

### Release Workflow

```python
def prepare_release(version_type='minor'):
    """
    Prepare a new release.
    
    Args:
        version_type: One of 'major', 'minor', 'patch'
    """
    # 1. Determine new version number
    current_version = get_current_version()
    new_version = bump_version(current_version, version_type)
    
    # 2. Create release branch
    create_branch(f"release/{new_version}")
    
    # 3. Update version numbers in files
    update_version_files(new_version)
    
    # 4. Generate change log from commits
    generate_changelog(current_version, new_version)
    
    # 5. Run automated tests
    run_test_suite()
    
    # 6. Build release candidate
    build_release_candidate(new_version)
    
    # 7. Deploy to staging environment
    deploy_to_staging(new_version)
    
    print(f"Release {new_version} is ready for final testing")
    
def finalize_release(version):
    """
    Finalize a release after testing.
    
    Args:
        version: The version to release
    """
    # 1. Final verification
    verify_release_candidate(version)
    
    # 2. Merge release branch to main
    merge_to_main(f"release/{version}")
    
    # 3. Tag the release
    create_tag(version)
    
    # 4. Merge release branch to develop
    merge_to_develop(f"release/{version}")
    
    # 5. Build final release assets
    build_release(version)
    
    # 6. Publish release
    publish_release(version)
    
    # 7. Announce release
    announce_release(version)
    
    print(f"Release {version} has been finalized and published")
```

### Changelog Management

A comprehensive changelog is maintained for each release with the following sections:

1. **Added**: New features
2. **Changed**: Changes in existing functionality
3. **Deprecated**: Features that will be removed in upcoming releases
4. **Removed**: Features removed in this release
5. **Fixed**: Bug fixes
6. **Security**: Vulnerability fixes

Example changelog entry:

```markdown
## [1.2.0] - 2025-09-15

### Added
- Multi-voice support for text-to-speech
- New plugin API for calendar integration
- Support for custom wake words

### Changed
- Improved speech recognition accuracy
- Optimized startup time by 30%
- Updated audio processing library to v3.1.0

### Fixed
- Memory leak in notification system
- Incorrect handling of timezone conversions
- GUI freeze when processing large audio files

### Security
- Updated OpenSSL to address CVE-2025-1234
```

## API Versioning

### API Version Management

The VPA system implements API versioning to allow for evolution while maintaining backward compatibility:

1. **URL Path Versioning** for REST APIs:
   - Format: `/api/v{major-version}/resource`
   - Example: `/api/v1/conversations`

2. **Content Type Versioning** for complex payload changes:
   - Format: `application/vnd.vpa.{resource}.v{major-version}+json`
   - Example: `application/vnd.vpa.command.v2+json`

3. **Plugin API Versioning**:
   - Plugin manifest specifies supported API versions
   - Core system validates compatibility before loading plugins

### API Deprecation Process

1. **Mark as Deprecated**:
   - Add `@Deprecated` annotation in code
   - Document in API reference with migration path
   - Return deprecation warning in responses

2. **Deprecation Timeline**:
   - Minor releases: Announce deprecation
   - Major releases: Remove deprecated features

3. **Support Policy**:
   - Major API versions supported for at least 12 months
   - Deprecated features supported for at least two minor releases

## Component Versioning

### Core System Components

Core system components follow the main application version number but maintain internal version tracking for dependencies:

```python
class ComponentVersionInfo:
    """Version information for a system component."""
    
    def __init__(self, component_name, version):
        self.component_name = component_name
        self.version = version
        self.api_version = self._derive_api_version(version)
        self.min_app_version = None
        self.max_app_version = None
        self.dependencies = {}
        
    def _derive_api_version(self, version):
        """Derive the API version from the component version."""
        # API version is the MAJOR.MINOR part of the component version
        parts = version.split('.')
        return f"{parts[0]}.{parts[1]}"
        
    def add_dependency(self, component_name, min_version, max_version=None):
        """Add a dependency on another component."""
        self.dependencies[component_name] = {
            'min_version': min_version,
            'max_version': max_version
        }
        
    def is_compatible_with_app(self, app_version):
        """Check if the component is compatible with the app version."""
        if not self.min_app_version:
            return True
            
        if semver.compare(app_version, self.min_app_version) < 0:
            return False
            
        if self.max_app_version and semver.compare(app_version, self.max_app_version) > 0:
            return False
            
        return True
        
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            'component_name': self.component_name,
            'version': self.version,
            'api_version': self.api_version,
            'min_app_version': self.min_app_version,
            'max_app_version': self.max_app_version,
            'dependencies': self.dependencies
        }
```

### Plugin Versioning

Plugins maintain their own version numbers independent of the core application:

```json
{
  "plugin_id": "com.example.calendar",
  "name": "Calendar Integration",
  "version": "1.3.2",
  "api_compatibility": {
    "min_version": "1.0.0",
    "max_version": "1.9.999"
  },
  "dependencies": [
    {
      "plugin_id": "com.example.notifications",
      "min_version": "1.1.0"
    }
  ]
}
```

## Database and Schema Versioning

### Schema Version Tracking

The database schema is versioned independently from the application with automated migration:

```python
class DatabaseSchema:
    """Database schema version and migration management."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._initialize_version_table()
        
    def _initialize_version_table(self):
        """Ensure the version table exists."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version_id INTEGER PRIMARY KEY,
                version TEXT NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        
    def get_current_version(self):
        """Get the current schema version."""
        result = self.db.execute("""
            SELECT version FROM schema_version 
            ORDER BY version_id DESC LIMIT 1
        """).fetchone()
        
        if result:
            return result[0]
        return "0.0.0"  # Initial version
        
    def migrate_to_version(self, target_version):
        """Migrate schema to the target version."""
        current = self.get_current_version()
        
        if semver.compare(current, target_version) == 0:
            print(f"Schema already at version {target_version}")
            return True
            
        if semver.compare(current, target_version) > 0:
            print(f"Downgrading schema from {current} to {target_version}")
            return self._downgrade_schema(current, target_version)
        else:
            print(f"Upgrading schema from {current} to {target_version}")
            return self._upgrade_schema(current, target_version)
            
    def _upgrade_schema(self, from_version, to_version):
        """Apply upgrades to reach target version."""
        # Implementation omitted for brevity
        pass
        
    def _downgrade_schema(self, from_version, to_version):
        """Apply downgrades to reach target version."""
        # Implementation omitted for brevity
        pass
        
    def record_migration(self, version, description):
        """Record a migration in the version table."""
        self.db.execute("""
            INSERT INTO schema_version (version, description)
            VALUES (?, ?)
        """, (version, description))
        self.db.commit()
```

### Data Migration Strategy

1. **Forward-Only Migrations**: Regular updates only support forward migration
2. **Backup Before Migration**: System creates automatic backups before schema changes
3. **Migration Testing**: All migrations tested on a copy of production data
4. **Rollback Plan**: Each migration includes a verified rollback procedure

## Configuration File Versioning

Configuration files include version information to ensure compatibility:

```yaml
# VPA Configuration File
version: 1.2.0
last_modified: 2025-09-01T10:30:00Z

# System Settings
system:
  log_level: info
  data_directory: ./data
  temp_directory: ./temp
  
# Audio Settings
audio:
  input_device: default
  output_device: default
  voice_profile: natural
  volume: 80
```

The application validates configuration file versions before loading:

```python
def load_config(config_path):
    """Load and validate configuration file."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Validate config version
    if 'version' not in config:
        raise ValueError("Missing version in configuration file")
        
    app_version = get_app_version()
    config_version = config['version']
    
    # Check compatibility
    if not is_config_compatible(app_version, config_version):
        print(f"Warning: Configuration version {config_version} may not be fully compatible with app version {app_version}")
        
        # Auto-upgrade if possible
        if can_auto_upgrade_config(config_version, app_version):
            config = upgrade_config(config, app_version)
            print(f"Configuration auto-upgraded to version {app_version}")
            
    return config
```

## Dependency Management

### Internal Dependencies

Internal dependencies are managed through explicit versioning in component manifests:

```json
{
  "component": "AudioSystem",
  "version": "1.3.0",
  "dependencies": {
    "EventSystem": ">=1.2.0 <2.0.0",
    "ConfigManager": ">=1.0.0",
    "ErrorHandler": ">=1.1.0"
  }
}
```

### External Dependencies

External dependencies are pinned to specific versions in requirements files with a clear update process:

**Python dependencies (requirements.txt)**:
```
# Core dependencies
pydantic==2.0.3
fastapi==0.104.1
sqlalchemy==2.0.23

# Audio processing
pyaudio==0.2.13
speechrecognition==3.10.0
pyttsx3==2.90
```

**Version update workflow**:

1. Regular security scans of dependencies
2. Scheduled dependency reviews every quarter
3. Automated testing with new dependency versions
4. Clear documentation of breaking changes

## Version Discovery and Reporting

### Version Information API

The system provides an API for retrieving version information:

```python
@app.get("/api/v1/system/version")
def get_version_info():
    """Get detailed version information about the system."""
    return {
        "application": {
            "name": "VPA",
            "version": "1.2.3",
            "build": "20250829-commit-a7d3b",
            "build_date": "2025-08-29T15:30:00Z"
        },
        "components": [
            {
                "name": "CoreSystem",
                "version": "1.2.3",
                "api_version": "1.2"
            },
            {
                "name": "AudioSystem",
                "version": "1.3.0",
                "api_version": "1.3"
            },
            # More components...
        ],
        "plugins": [
            {
                "id": "com.example.calendar",
                "name": "Calendar Integration",
                "version": "1.3.2"
            },
            # More plugins...
        ],
        "database_schema": "1.4.0",
        "config_version": "1.2.0"
    }
```

### Debug Information

For troubleshooting, the system provides detailed version information in logs:

```
[2025-08-29 15:30:00] [INFO] VPA System starting up
[2025-08-29 15:30:00] [INFO] Application version: 1.2.3 (build 20250829-commit-a7d3b)
[2025-08-29 15:30:00] [INFO] Database schema version: 1.4.0
[2025-08-29 15:30:00] [INFO] Configuration version: 1.2.0
[2025-08-29 15:30:01] [INFO] Loaded components: CoreSystem v1.2.3, AudioSystem v1.3.0, GUISystem v1.1.2
[2025-08-29 15:30:02] [INFO] Loaded plugins: Calendar Integration v1.3.2, Weather v2.0.1
```

## Update and Rollback Procedures

### Update Process

The system implements a staged update process:

```python
def update_system(target_version):
    """Update the system to a new version."""
    current_version = get_current_version()
    
    if semver.compare(current_version, target_version) == 0:
        print(f"System already at version {target_version}")
        return True
        
    print(f"Updating from {current_version} to {target_version}")
    
    # 1. Verify update package
    if not verify_update_package(target_version):
        print("Update package verification failed")
        return False
        
    # 2. Create backup
    backup_path = create_system_backup(current_version)
    print(f"System backup created at {backup_path}")
    
    # 3. Stop services
    stop_services()
    
    try:
        # 4. Apply updates to files
        apply_file_updates(target_version)
        
        # 5. Update database schema
        update_database_schema(target_version)
        
        # 6. Update configuration
        update_configuration(target_version)
        
        # 7. Start services
        start_services()
        
        # 8. Verify system health
        if verify_system_health():
            print(f"System successfully updated to {target_version}")
            return True
        else:
            print("System health check failed, rolling back")
            rollback_update(current_version, backup_path)
            return False
            
    except Exception as e:
        print(f"Update failed: {e}")
        rollback_update(current_version, backup_path)
        return False
```

### Rollback Process

In case of update failure, the system can be rolled back:

```python
def rollback_update(previous_version, backup_path):
    """Roll back to the previous version."""
    print(f"Rolling back to version {previous_version}")
    
    # 1. Stop services
    stop_services()
    
    try:
        # 2. Restore from backup
        restore_from_backup(backup_path)
        
        # 3. Start services
        start_services()
        
        # 4. Verify system health
        if verify_system_health():
            print(f"System successfully rolled back to {previous_version}")
            return True
        else:
            print("System health check failed after rollback")
            return False
            
    except Exception as e:
        print(f"Rollback failed: {e}")
        print("Manual intervention required")
        return False
```

## Development Workflow

### Feature Development Cycle

```
┌─────────────────────┐
│ Create feature      │
│ branch from develop │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Implement feature   │
│ with tests          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Regular commits     │
│ with proper format  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Create pull request │
│ to develop          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Code review and     │
│ automated tests     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Address feedback    │
│ and revise code     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Merge to develop    │
│ when approved       │
└─────────────────────┘
```

### Version Bumping

Version numbers are updated according to the following rules:

1. **Manual Decisions**:
   - Major version bumps require team discussion and planning
   - Minor version bumps decided during sprint planning
   - Patch version bumps determined during release preparation

2. **Automated Assistance**:
   - Commit message analysis suggests version impacts
   - CI/CD pipeline validates version changes

### Continuous Integration

The CI system enforces versioning rules:

1. **Version Validation**:
   - Ensures version numbers are correctly incremented
   - Validates that CHANGELOG.md is updated
   - Confirms version consistency across components

2. **Release Tagging**:
   - Automatically creates git tags for releases
   - Generates release notes from changelog

## Version Compatibility

### Backward Compatibility Policy

1. **API Compatibility**:
   - Minor and patch releases must maintain backward compatibility
   - Breaking changes require a major version increment
   - Deprecated features removed only in major versions

2. **Data Format Compatibility**:
   - Data schema changes must be backward compatible in minor releases
   - Forward migration support required for all releases
   - Backward migration support required for major releases

### Forward Compatibility

The system implements a "tolerant reader" approach:

1. **Unknown Properties**:
   - Ignore unknown properties in input data
   - Preserve unknown properties when updating existing data

2. **Feature Detection**:
   - Components detect available features rather than version checking
   - Graceful fallback when features are unavailable

## References

- DEPENDENCY_MANAGEMENT.md - For detailed dependency management strategy
- API_SPECIFICATIONS.md - For API design and versioning approach
- ERROR_HANDLING_STRATEGY.md - For error handling during upgrades and rollbacks
- PLUGIN_ARCHITECTURE.md - For plugin compatibility requirements

---

*Document created: August 29, 2025*
