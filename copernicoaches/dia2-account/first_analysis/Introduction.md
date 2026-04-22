# Introduction

## What this dataset contains

This package defines one self-contained change scenario for the workshop.

It combines three types of artifacts:

1. **Process definition**
   - `AC_CheckAccountBalance.drawio`
   - Describes the workflow, decisions, branches and expected outputs.

2. **UI/business data forms**
   - `forms/*.json`
   - Define the structured business objects used as case forms.

3. **Backend service contracts**
   - `swagger/*.json`
   - Define the APIs used to read and persist case data, retrieve balances and query calendars.

Taken together, these artifacts describe both the behavior to implement and the data/services that implementation depends on.

## How to read the package

The package should be read from process to data to services.

### First: process
Start with the process diagram. It explains the business intention and the branching logic:
- read forms
- resolve account id
- retrieve balances
- decide the action
- possibly calculate a working date
- persist data or errors
- return the final action

See: `Process.md`

### Second: UI/data
Then inspect the form files. They explain where the process reads from and writes to:
- form 1 = common case context
- form 2 = contracts/accounts
- form 3 = account closure working data
- form 4 = errors

See: `UI.md`

### Third: services
Finally inspect the service contracts. They explain how the process interacts with backend systems:
- read/write case additional data
- retrieve account balances
- retrieve calendar dates

See: `Services.md`

## Recommended implementation view

A reasonable implementation model for this dataset is:

1. Load case forms 1, 2 and 3.
2. Extract the account identifier from form 2.
3. Call the balances endpoint.
4. Update form 3 with the initial balance.
5. Apply the branching rules from the diagram.
6. If necessary, call the calendar endpoint and compute `dateToCheckBalance`.
7. Persist updated form data.
8. On failure, persist form 4 with structured error information.
9. Return a compact process result containing `action` and optional `dateTime`.

## Relationship between the four documents

- **`Process.md`** explains the workflow and business rules.
- **`UI.md`** explains the form structures and their role in the process.
- **`Services.md`** explains the APIs required by the process.
- **`Introduction.md`** ties the three layers together.

## Why this is useful in the workshop

This dataset is a good workshop case because it is not just a feature request. It already includes the three layers that teams usually have to reconstruct from scattered sources:

- business flow
- data structures
- technical service definitions

That makes it suitable for exercises in:
- operational reading of a problem
- context engineering
- transformation into human-readable artifacts
- specification building
- later implementation and testing

## Main unresolved points

The package is strong enough for workshop use, but not perfectly implementation-ready. Before building production code, the team should resolve at least these questions:

- Is `contracts[1]` intentional, or should the process choose a contract dynamically?
- Which balance item should be selected when the service returns multiple balances?
- What is the exact payload shape expected by `additional_data` updates?
- Which service façade is authoritative for case additional data?
- What exact success and error semantics should be used for persistence calls?

Those ambiguities are not a flaw for the workshop. They are part of what makes the case useful.
