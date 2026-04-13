## ADDED Requirements

### Requirement: Active directory full path is visible above the table
The system MUST render the complete active directory path in a dedicated line above the Miller Columns table.

#### Scenario: User navigates to a child directory
- **WHEN** the user enters a directory using keyboard navigation
- **THEN** the header line above the table MUST display the full path of that directory

#### Scenario: User navigates to parent directory
- **WHEN** the user returns to the parent directory
- **THEN** the header line above the table MUST update to the parent full path

### Requirement: Full path rendering does not modify navigation behavior
The system MUST preserve existing keyboard navigation and selection behavior when showing the full path header.

#### Scenario: User navigates with arrow keys
- **WHEN** the user moves selection and enters/exits directories with arrow keys
- **THEN** navigation behavior MUST remain unchanged
- **AND** only the additional header line with full path is introduced visually