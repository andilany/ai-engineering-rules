+++
id = "data.postgresql"
title = "PostgreSQL"
severity = "preferred"
scopes = ["data"]
+++
# PostgreSQL

- Prefer PostgreSQL for greenfield relational domains when no database has already been selected.
- Never migrate an existing MongoDB or other store to PostgreSQL solely because PostgreSQL is preferred.
- Design constraints, indexes, transactions, isolation, and concurrency at the database level where correctness depends on them.
