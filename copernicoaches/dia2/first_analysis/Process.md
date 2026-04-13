# Process

## Purpose

This document explains the business flow captured in `AC_CheckAccountBalance.drawio`. The process is an automatic task that checks the balance of an account linked to a case and returns an action that drives the next step in the case workflow.

The diagram is centered on one operational question: what should the case do after checking the account balance?

## Inputs

The flow starts from a case/task payload similar to:

```json
{
  "case": {
    "caseId": "92837589263",
    "process": {
      "processId": "00141"
    }
  },
  "taskId": "3-1",
  "data": ""
}
```

The diagram also states that the process reads case additional data from forms **1**, **2** and **3**.

## Relevant form data used by the process

- **Form 1 — commonData**
  - `source`
- **Form 2 — contracts**
  - `contracts[1].contractId` is used as the source `account_id`
- **Form 3 — accountClosure**
  - `initialBalance`
  - `settlementResult.balanceResult.amount`
  - `dateToCheckBalance`
  - `entity`

## Main flow

### 1. Read current case data

The process first reads additional data for the case and expects forms 1, 2 and 3 to be available.

### 2. Resolve the account and retrieve balances

The account identifier comes from:

- `form 2 -> metaData.contracts[1].contractId`

Then the process calls the balance API:

- `GET /v3/account_balances_transactions_holds/{accountId}/balances`

The returned balance is stored back into form 3:

- `formReference = 3`
- `metaData.initialBalance.amount`
- `metaData.initialBalance.currency`

If the save fails, the execution must stop and return the same error received from the service.

### 3. Evaluate the balance

The core branching logic is:

- If balance is **greater than 0** → action = `positiveBalance`
- If balance is **equal to 0** → action = `zeroBalance`
- If balance is **less than 0** → continue with extra checks

## Negative balance logic

When the balance is negative, the process inspects the origin of the case.

### Branch A — source is `CLI`

The diagram explicitly marks:

- `form 1 -> metaData.source = "CLI"`

In that case the action becomes:

- `customerNegativeBalance`

### Branch B — source is not `CLI`

The action becomes:

- `bankNegativeBalance`

There is one additional condition in the diagram:

- `form3.dateToCheckBalance != empty`

This creates a waiting/cancel path.

## Waiting and cancellation path

If `form3.dateToCheckBalance` is already present, the process compares it with the current day:

- if `dateToCheckBalance = today` → action = `cancel`
- otherwise → action = `wait` and `dateTime = tomorrow 00:01`

If `dateToCheckBalance` is not present, the process calculates it from a parameter `daysToCheckBalance` expressed in working days.

To do that, it retrieves calendar information and computes the exact future working day.

## Calendar-dependent calculation

The diagram includes:

- check parameter `daysToCheckBalance (work days)`
- get non-working days for the following weeks
- calculate the exact working day from `today + daysToCheckBalance`

Calendar selection depends on the entity in form 3:

- if `Entity = 0014` → `calendarId = 3`
- if `Entity = ZE00` → `calendarId = 1`

The calendar API shown in the dataset is:

- `GET /v1/calendars/{calendar_id}/dates`

Once the date is calculated, it is persisted through the additional data update API.

## Persistence behavior

The diagram repeatedly uses:

- `PUT /case_management/cases/{caseId}/additional_data`

This is used to persist at least:

- form 3 updated `initialBalance`
- form 3 updated `dateToCheckBalance`
- possibly other metadata required by the task state

The diagram also says that on non-200 responses the process must:

- stop execution
- return the same error
- save error information before exiting

## Error handling

On errors, the flow stores an error payload in form 4 (`errorsInformation`) with a structure equivalent to:

```json
{
  "taskName": "Automatic Task Check Balance",
  "dateTime": "<now()>",
  "cancellable": "0",
  "errors": [
    {
      "code": "400",
      "description": "Bad request",
      "level": "ERROR",
      "message": "1652430533435 Open flow bad request"
    }
  ]
}
```

## Output contract

The final process output described in the diagram is:

```json
{
  "data": {
    "action": "positiveBalance | customerNegativeBalance | bankNegativeBalance | zeroBalance | wait | cancel",
    "dateTime": ""
  }
}
```

## Notes and ambiguities

The draw.io file is useful but not fully precise. These points should be clarified before implementation:

1. The diagram uses `contracts[1].contractId`. It is unclear whether that means the first element, the second element, or a fixed business convention.
2. The source of the balance amount is shown as `balances[0].amount.amount`, but the rule for selecting the right balance entry is not stated.
3. The branch between `customerNegativeBalance` and `bankNegativeBalance` is driven by `source`, but the exact full list of source values is not documented.
4. The persistence payload shown in Swagger uses `metaData.businessData` / `filters`, while the diagram speaks in terms of direct `metaData.<field>` updates. That mapping needs to be standardized.
5. The exact status code expected by the update endpoint is inconsistent between diagram notes and Swagger examples.
