## ADDED Requirements

### Requirement: Item list shows folder icon for directories
The system MUST render a folder icon prefix for every directory entry shown in Miller columns.

#### Scenario: Directory entry is displayed
- **WHEN** a column renders an entry whose type is directory
- **THEN** the visible label MUST include the configured folder icon prefix before the entry name

### Requirement: Item list shows file icon for files
The system MUST render a file icon prefix for every file entry shown in Miller columns.

#### Scenario: File entry is displayed
- **WHEN** a column renders an entry whose type is file
- **THEN** the visible label MUST include the configured file icon prefix before the entry name

### Requirement: Icons do not alter navigation behavior
The system MUST preserve existing navigation and selection behavior when icons are enabled.

#### Scenario: User navigates with arrow keys
- **WHEN** the user moves selection and enters/exits directories using arrow keys
- **THEN** behavior MUST remain unchanged compared with rendering without icons
- **AND** only the visual label content differs by adding type icon prefixes
