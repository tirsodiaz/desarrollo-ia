## ADDED Requirements

### Requirement: Selection Counter Is Inline With Header Status
The renderer MUST display the selected-item counter in the same visual line as the header status text (for example, route or drive context), and MUST NOT render that counter as an independent line below the help footer.

#### Scenario: Render with selected entry
- **WHEN** there are visible entries and `selected_index` points to a valid item
- **THEN** the output includes a single status line containing both context text and `[n/N]`
- **THEN** no standalone line containing only `[n/N]` is rendered in footer position

#### Scenario: Render with no selectable entries
- **WHEN** the current content list is empty or `selected_index` is invalid
- **THEN** the status line is rendered without `[n/N]`
- **THEN** the footer remains reserved for help and optional error text only

### Requirement: Navigation Help Text Is Standardized
The renderer MUST show the navigation help text exactly as `up/down mover . -> entrar . <- volver . Esc salir` as visible guidance for user input actions.

#### Scenario: Normal render state
- **WHEN** the screen is rendered in any navigation state without fatal error
- **THEN** the footer includes `up/down mover . -> entrar . <- volver . Esc salir`

#### Scenario: Render with error message
- **WHEN** an error message is present in state
- **THEN** the navigation help text remains visible
- **THEN** the error message is shown in addition to the help text
