# What does "Check Account Balance" actually do?

## The short version

When a customer asks to close their bank account, the bank cannot simply close it on the spot. One of the first things the system needs to know is: **what is the current balance of that account?**

This automatic step — called *Check Account Balance* — does exactly that. It reads the balance, makes a decision based on what it finds, and tells the rest of the process what to do next.

No human intervenes. It runs automatically as part of the account closure workflow.

---

## What triggers it?

The process is triggered by the case management system as soon as the account closure case reaches this step. It receives just enough information to know which case and which task it is dealing with. Everything else it needs, it goes and fetches itself.

---

## What does it do, step by step?

### Step 1 — Read the case file

The process first opens the case file (stored in the system) and reads three pieces of information:

- **Who is the customer and what is the source of the request?** Was it the customer who asked to close the account, or was it the bank's own initiative?
- **Which account needs to be checked?** This is taken from the list of contracts linked to the case.
- **Has a "check date" already been set?** This would mean the process has run before and is waiting to check again on a specific date.

### Step 2 — Fetch the live account balance

With the account number in hand, the process calls the bank's account system to get the current balance in real time.

It then saves that balance back into the case file for reference.

### Step 3 — Make a decision

This is the heart of the process. It looks at the balance and decides which path the case should follow:

| Balance situation | What happens next |
|---|---|
| Balance is **positive** (money in the account) | The account has funds — case moves to the "positive balance" step |
| Balance is **exactly zero** | The account is empty — case moves to the "zero balance" step |
| Balance is **negative** (the customer owes money) | More checks are needed — see below |

### Step 4 — What happens when the balance is negative?

A negative balance means the customer owes the bank money. The action the system takes depends on **who initiated the closure**:

- **Customer-initiated closure** (e.g. from an online portal or branch): the case is marked as `customerNegativeBalance` — the bank handles it knowing the customer is aware
- **Bank-initiated closure** (internal process): the case is marked as `bankNegativeBalance` — a different handling process takes over

In both negative-balance cases, the system also checks whether there is a **scheduled re-check date** on the case:

| Date situation | What happens next |
|---|---|
| No re-check date has been set yet | Calculate a future working date (using a configurable number of working days and a calendar) and save it on the case. The case is put on hold (`wait`) until tomorrow, when it will pick up from there |
| A re-check date exists and it is **today** | The waiting period is over — the case is marked `cancel` |
| A re-check date exists but it is **not yet today** | Still waiting — action = `wait`, check again tomorrow at 00:01 |

### Step 5 — Save and report

Whatever the outcome, the process writes its findings back to the case and returns a compact result to the workflow engine:

- **What action should the case take next** (one of: `positiveBalance`, `zeroBalance`, `customerNegativeBalance`, `bankNegativeBalance`, `wait`, `cancel`)
- **When to resume** (only relevant for the `wait` action — set to tomorrow at 00:01)

If anything goes wrong (the balance system is unavailable, the case data is missing, etc.), the process saves a structured error record on the case and stops. The error is visible to operators for investigation.

---

## In plain terms: what question does this step answer?

> *"Should we proceed with closing the account now, or is there an obstacle — and if so, what kind?"*

The answer drives the entire subsequent handling of the account closure case.

---

## What the process does NOT do

- It does **not** close the account. That happens later, in other steps.
- It does **not** contact the customer. It is a fully automated background check.
- It does **not** make a judgement call. All decisions are rule-based (balance above zero, equal to zero, below zero; source of request; today's date vs. scheduled date).

---

## Open questions that a business owner should resolve

Before this process goes into production, the following points need a clear answer from the business side:

1. **Which contract/account is checked?** The system currently picks the second entry in the contract list. Is that always the right account, or should it pick the account dynamically based on some rule?
2. **Which balance figure counts?** The bank system can return multiple balance types for the same account. The business needs to specify which one (e.g. current available balance, booked balance) is the authoritative one for this decision.
3. **How many working days to wait?** The number of days before re-checking a negative-balance account is a configurable parameter. The business must define its value.
4. **What counts as "bank-initiated" vs "customer-initiated"?** The process currently distinguishes based on a single source code (`CLI` = customer). If other channels exist, the mapping needs to be complete.
