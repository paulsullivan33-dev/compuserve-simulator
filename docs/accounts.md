# Accounts and login

## Accounts and login

Enter `CIS` at the Host Name prompt (or press Enter) to log in. Enter `PHONES`
to browse the access-number directory without an account. Search by full or partial
city name, optionally including the state/province abbreviation (for example,
`Portland, OR`). `ALL` lists cities in pages; Enter advances, `S` starts another
search, and `M` returns to Host Name. At the city prompt, blank input also returns.
Search ignores case, accents and punctuation; `NYC`, `LA`, `SF`, and `DC` work too.

The directory covers major U.S. cities, all 50 states, DC, and Canadian centers.
Every number is marked `HISTORICAL` or `FICTIONAL`. Historical entries come from
CompuServe's [March 1, 1983 access-number sheet, page 1](https://www.pagetable.com/docs/cbm1600modem/compuserve2.pdf)
and retain its original area codes (CNS, 300 baud); they are not a verified 1988
or current directory. Supplemental cities use fictional `555-01xx` numbers.
`SOURCES` displays the reference inside PHONES. This directory only displays
numbers; it does not dial them or change the session's baud setting.

User IDs use the form `70000,0001`. Existing
legacy accounts establish a local password on their next login. Unknown IDs can create
a new local account. Passwords are stored as salted PBKDF2 hashes, never as plain text.
Three failed attempts lock the account until a local SysOp unlocks it.

User ID `77777,0001` is designated as the initial local SysOp account. Its password is
established on first login.

---

[Back to the user guide](../USER_GUIDE.md)
