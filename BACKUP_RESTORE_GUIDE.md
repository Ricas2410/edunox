# Edunox GH - Backup and Restore System

## Overview

This system provides robust backup and restore functionality that works across different database engines (SQLite, PostgreSQL, MySQL, etc.). The system is designed to be database-agnostic, allowing you to backup from one database type and restore to another.

## Features

- **Cross-Database Compatibility**: Backup from SQLite and restore to PostgreSQL (and vice versa)
- **Complete Data Backup**: All application data including users, services, bookings, FAQs, etc.
- **Media Files Support**: Optional backup and restore of uploaded files
- **Compression Support**: Optional ZIP compression for easy storage and transfer
- **Metadata Tracking**: Backup includes metadata for verification and compatibility checking
- **Safe Restore**: Options for dry-run and selective restore
- **Transaction Safety**: All restore operations are wrapped in database transactions

## Commands

### Backup Data

```bash
# Basic backup
python manage.py backup_data

# Backup with media files
python manage.py backup_data --include-media

# Backup to specific directory
python manage.py backup_data --output /path/to/backups

# Compressed backup
python manage.py backup_data --compress --include-media
```

### Restore Data

```bash
# Basic restore (adds to existing data)
python manage.py restore_data /path/to/backup

# Restore from ZIP file
python manage.py restore_data /path/to/backup.zip

# Complete restore (clears existing data first) - DANGEROUS!
python manage.py restore_data /path/to/backup --clear-existing

# Restore with media files
python manage.py restore_data /path/to/backup --include-media

# Dry run (see what would be restored)
python manage.py restore_data /path/to/backup --dry-run
```

## Backup Structure

```
Edunox_backup_20250124_143022/
├── backup_metadata.json          # Backup information and metadata
├── data/                         # Database data (JSON format)
│   ├── core.json                # Core app data (FAQs, site config)
│   ├── accounts.json            # User accounts and profiles
│   ├── services.json            # Services and categories
│   ├── bookings.json            # Booking data
│   └── ...                      # Other app data
└── media/                       # Media files (if --include-media used)
    ├── profile_pictures/
    ├── documents/
    └── ...
```

## Cross-Database Migration Example

### Scenario: Moving from SQLite (Development) to PostgreSQL (Production)

1. **Create backup from SQLite**:
   ```bash
   python manage.py backup_data --compress --include-media --output ./migration_backup
   ```

2. **Setup PostgreSQL database** with same Django models

3. **Restore to PostgreSQL**:
   ```bash
   python manage.py restore_data ./migration_backup/Edunox_backup_*.zip --include-media
   ```

The system automatically handles:
- Data type conversions
- Primary key mapping
- Foreign key relationships
- Field compatibility

## Safety Features

### Backup Safety
- Non-destructive operation
- Preserves original data
- Includes verification metadata
- Atomic file operations

### Restore Safety
- Transaction-wrapped operations (rollback on failure)
- Dry-run capability
- Confirmation prompts for destructive operations
- Field compatibility checking
- Graceful error handling

## Professional FAQ Content

The system includes a comprehensive set of professional FAQs that:

### Clearly Establish Independence
- Explicitly states Edunox GH is NOT affiliated with any university
- Clarifies the role as an independent consultancy service
- Distinguishes between education providers and support services

### Transparent About Fees
- Explains why fees are charged for free university applications
- Details what services are included in fees
- Clarifies that fees are for consultancy, not education

### Educational Guidance
- Provides information about university application processes
- Explains scholarship and financial aid assistance
- Covers digital literacy training and support

### Trust and Transparency
- Addresses legitimacy concerns
- Provides clear service expectations
- Includes satisfaction guarantees

## Usage Examples

### Regular Backup Schedule
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
python manage.py backup_data --compress --include-media --output /backups/daily/
```

### Migration Script
```bash
#!/bin/bash
# Complete migration from development to production
echo "Creating backup from development database..."
python manage.py backup_data --compress --include-media --output ./migration

echo "Restoring to production database..."
python manage.py restore_data ./migration/Edunox_backup_*.zip --clear-existing --include-media

echo "Migration complete!"
```

### Disaster Recovery
```bash
# Restore from latest backup
LATEST_BACKUP=$(ls -t /backups/*.zip | head -1)
python manage.py restore_data "$LATEST_BACKUP" --clear-existing --include-media
```

## Best Practices

### Backup Best Practices
1. **Regular Backups**: Schedule daily/weekly backups
2. **Multiple Locations**: Store backups in multiple locations
3. **Test Restores**: Regularly test restore procedures
4. **Include Media**: Always backup media files for complete restore
5. **Compress**: Use compression for storage efficiency

### Restore Best Practices
1. **Dry Run First**: Always test with --dry-run
2. **Backup Before Restore**: Create backup before major restores
3. **Verify Data**: Check data integrity after restore
4. **Test Functionality**: Verify application works after restore
5. **Monitor Logs**: Check for any restore warnings or errors

## Troubleshooting

### Common Issues

**Backup fails with permission error**:
```bash
# Ensure backup directory is writable
chmod 755 /path/to/backup/directory
```

**Restore fails with foreign key error**:
- The system handles dependencies automatically
- If issues persist, try restoring with --clear-existing

**Media files not restored**:
- Ensure --include-media flag is used for both backup and restore
- Check media directory permissions

**Cross-database restore issues**:
- Verify target database is properly configured
- Ensure all required Django apps are installed
- Run migrations before restore: `python manage.py migrate`

## Security Considerations

- Backup files contain sensitive data - store securely
- Use encryption for backup storage in production
- Limit access to backup/restore commands
- Regularly rotate backup encryption keys
- Audit backup and restore operations

## Support

For issues with the backup/restore system:
1. Check the backup metadata for compatibility information
2. Use --dry-run to test restore operations
3. Verify database connectivity and permissions
4. Check Django logs for detailed error information
