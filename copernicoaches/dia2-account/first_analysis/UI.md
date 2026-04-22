# UI

## Purpose

This document summarizes the UI-related structures found in the `forms/` directory. These JSON files are not front-end screens by themselves. They are structured data schemas that define the business objects the UI and the process work with.

The dataset contains four form definitions:

- `commonData.json` → form 1
- `contracts.json` → form 2
- `accountClosure.json` → form 3
- `errorsInformation.json` → form 4

## Form 1 — commonData

**File:** `commonData.json`  
**Form reference:** `1`  
**Logical name:** `commonData`

### Main fields
- `applicants[]`
- `process.processId`
- `status.code`
- `status.stage.code`
- `status.stage.validityPeriod.startDate`
- `status.validityPeriod.startDate`
- `externalReference`
- `validityPeriod.startDateTime`
- `validityPeriod.endDateTime`
- `channel`
- `source`

### Why it matters in the process
The draw.io file explicitly uses:

- `source`

This field is part of the branching logic for negative balances.

## Form 2 — contracts

**File:** `contracts.json`  
**Form reference:** `2`  
**Logical name:** `contracts`

### Main fields
- `contracts[]`
  - `contractId`
  - `product.productCode`
  - `product.productDescription`
  - `closeDate`
  - `participants[]`
  - `balances[]`

### Why it matters in the process
The draw.io file uses:

- `contracts[1].contractId`

That value is used as the input `account_id` for the balance service call.

## Form 3 — accountClosure

**File:** `accountClosure.json`  
**Form reference:** `3`  
**Logical name:** `accountClosure`

### Main fields
- `caseSourceId`
- `requestedAccountClosureDate`
- `accountClosureReasonId`
- `confirmationLetterRequested`
- `caseNotInScope`
- `accountsToTransfer[]`
- `settlementResult`
  - `amount`
  - `balanceResult`
  - `date`
- `initialBalance`
  - `amount`
  - `currency`
- `communicationsToCustomer`
- `dateToCheckBalance`
- `dateToCheckTransactionPosting`
- `entity`

### Why it matters in the process
This is the main working form for the task.

The diagram uses or updates at least these fields:

- `initialBalance.amount`
- `initialBalance.currency`
- `settlementResult.balanceResult.amount`
- `dateToCheckBalance`
- `entity`

### Observed behavior from the diagram

- `initialBalance` is updated with the value returned by the balance API.
- `dateToCheckBalance` is used to decide between `wait` and `cancel`.
- `entity` drives calendar selection.
- `settlementResult.balanceResult.amount` is mentioned in the diagram as a balance-related field to inspect in one branch.

## Form 4 — errorsInformation

**File:** `errorsInformation.json`  
**Form reference:** `4`  
**Logical name:** `errorsInformation`

### Main fields
- `taskName`
- `dateTime`
- `cancellable`
- `errors[]`
  - `code`
  - `description`
  - `level`
  - `message`

### Why it matters in the process
The process diagram uses this form to persist service errors before returning a failed result.

## How these forms fit together

The four forms represent a layered UI/business-data model.

### Context layer
- **Form 1** stores case context and source metadata.

### Selection layer
- **Form 2** stores the contracts/accounts involved in the case.

### Execution layer
- **Form 3** stores the working state and the values that the automatic balance-check task updates.

### Error layer
- **Form 4** stores structured execution errors.

## Minimal UI interpretation

If someone had to implement a basic front-end from these schemas, the UI would likely need:

### Common data screen
- applicant data
- process/status information
- source/channel details

### Contracts screen
- list of contracts
- selected contract/account identifier
- product data
- existing balances if present

### Account closure screen
- closure request date
- closure reason
- initial balance
- settlement result
- waiting/check dates
- entity
- transfer targets and transfer amounts

### Error screen or technical panel
- task name
- timestamp
- cancellable flag
- structured error list

## Important caveat

These JSON files are schema-like business definitions, not full visual definitions. They do not specify:

- layout
- widgets
- validation messages
- visibility rules
- conditional sections
- navigation flow

So they should be treated as the **data contract behind the UI**, not as a finished screen model.
