# Services

## Purpose

This document summarizes the backend APIs present in the `swagger/` directory and highlights the ones that are directly relevant to the account balance checking flow.

The dataset contains three API definitions:

- `pbbaccounts-swagger.json`
- `pbbextendedcase-swagger.json`
- `pbbportalbff-swagger.json`

## Service groups

### 1. Accounts service

File: `pbbaccounts-swagger.json`

This API contains account-related operations: balances, transactions, holds, warning blocks, pending entries and parameter retrieval.

For the current process, the most relevant endpoint is:

#### Get account balances

- **Method:** `GET`
- **Path:** `/v3/account_balances_transactions_holds/{accountId}/balances`

**Parameters**
- `accountId` (path)
- `date` (query, optional ISO date)

**Response 200**
```json
{
  "balances": [
    {
      "amount": {
        "amount": 99.99,
        "currency": "EUR"
      },
      "creditDebitIndicator": "Credit",
      "typeCode": "CRRT",
      "typeDescription": "Current",
      "lastUpdateDate": "2025-01-01"
    }
  ]
}
```

**Error format**
```json
{
  "errors": [
    {
      "code": "string",
      "description": "string",
      "level": "string",
      "message": "string"
    }
  ]
}
```

### 2. Extended case service

File: `pbbextendedcase-swagger.json`

This API manages case-related additional business data.

For the current process, two operations matter most.

#### Read case additional data

- **Method:** `GET`
- **Path:** `/case_management/cases/{caseId}/additional_data`

**Parameters**
- `caseId` (path)
- `form_reference` (query)
- `_limit` (query)
- `_offset` (query)

**Response 200**
```json
{
  "_links": {},
  "additional_data": [
    {
      "formReference": "1",
      "metaData": {}
    }
  ]
}
```

#### Update case additional data

- **Method:** `PUT`
- **Path:** `/case_management/cases/{caseId}/additional_data`

**Parameters**
- `caseId` (path)

**Request body**
```json
{
  "formReference": "3",
  "metaData": {
    "businessData": {},
    "filters": {}
  }
}
```

The Swagger schema models `metaData` through a generic object named `BusinessMetaData` with two generic nodes:

- `businessData`
- `filters`

That is looser than the form JSON files, which define concrete business structures.

### 3. Portal/BFF service

File: `pbbportalbff-swagger.json`

This API is broader. It includes process/case operations, task actions, communication, token conversion, request proxying and calendars.

For the current process, the most relevant endpoint is:

#### Get calendar dates

- **Method:** `GET`
- **Path:** `/v1/calendars/{calendar_id}/dates`

**Parameters**
- `calendar_id` (path)
- `start_date` (query)
- `end_date` (query)
- `_limit` (query)
- `_offset` (query)

**Response 200**
```json
{
  "datesList": [
    {
      "date": "2023-10-01",
      "dateName": "Working day",
      "dateType": "Holiday"
    }
  ],
  "linksCalendarList": {}
}
```

This endpoint is the only calendar endpoint present in the dataset and matches the draw.io path that calculates a future working day.

## Cross-service role in the process

The intended orchestration is straightforward.

### Read phase
1. Read case forms from the case service.
2. Extract `contractId` from form 2.
3. Call the accounts service to obtain balances.

### Decision phase
4. Apply the flow logic from the process diagram.
5. Possibly call the calendar endpoint to calculate a working date.

### Write phase
6. Persist updates and error information back into case additional data.

## Relevant mismatches and implementation risks

### Generic case metadata vs concrete form schemas

The case API uses a very generic structure:

```json
{
  "formReference": "3",
  "metaData": {
    "businessData": {},
    "filters": {}
  }
}
```

But the form JSON files define strongly shaped business objects such as:

- `commonData`
- `contracts`
- `accountClosure`
- `errorsInformation`

The implementation will need a stable mapping between the generic API envelope and the actual form payload.

### Endpoint duplication

The portal BFF also exposes endpoints for case additional data:

- `GET /case_management/cases/{caseId}/additional_data`
- `PUT /case_management/cases/{caseId}/additional_data`

The dataset does not explain whether the process should use the BFF version, the extended case service version, or whether they are effectively the same façade.

### Response-code inconsistency

The draw.io notes refer several times to `response = 200`, while the Swagger for the `PUT additional_data` endpoint documents no 200 success body and instead returns `204` in one file. That must be normalized in implementation and tests.

## Minimum service contract needed by the workshop

For workshop purposes, the essential service contract can be reduced to four capabilities:

1. Read forms 1, 2 and 3 for a case.
2. Read account balances for a given `accountId`.
3. Read calendar dates to compute working days.
4. Persist updated form 3 and form 4 back into case data.
