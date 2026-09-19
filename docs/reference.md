# Reference Data Bases

## Reference Data Bases

The four classic Reference choices contain 200 records total, with 50 records apiece in Academic
American Encyclopedia, Medical Information, Science and Technology Index, and Electronic Library. Enter words
to search, `B` to browse the complete index, `H` for help, or `M` to return. Search
results display stable record identifiers and may be selected for the full entry. Result
lists show 12 records per page; use `F` and `B` to move between pages. A record ID such
as `L4003` may be entered directly. Boolean expressions support `AND`, `OR`, and `NOT`,
and displayed records include `SEE ALSO` cross-references derived from their descriptors.
Medical records are general historical-simulation information and are not a diagnosis.
Reference records are also included in the global `FIND words` command.

Reference content is stored separately in `reference_databases.json`. Startup validates
the four database names, record structure, unique identifiers, 50 records per database,
and the 200-record total before accepting the catalog.

Member research commands include `HISTORY`, `RECALL n`, `CLEAR HISTORY`, `MARK id`,
`MARKED`, and `DOWNLOAD`. The download command writes an ASCII marked-record packet in
the member download directory. `SUBJECTS` lists database-specific subject indexes and
`SUBJECT name` browses one. Relevant Reference record IDs may also appear as background
suggestions after a Forum post or beneath a News dispatch.

A fifth choice, Live General Reference, searches Wikipedia over the Internet and presents
up to 10 results in the same terminal style. Live records use `W` identifiers and are
clearly labeled as modern content outside the December 1988 simulation. The search waits
up to five seconds; if the provider or network is unavailable, the classic offline
databases remain usable. Results are cached in SQLite for 24 hours, and an older cached
copy is used when the provider is temporarily unavailable. `MARK n`, `MARKED`, and
`DOWNLOAD` preserve live records and include them in the same research packet as classic
records. No additional Python package or API key is required.

Live Academic Reference searches OpenAlex scholarly works and displays authors, source,
publication year, DOI, citations, open-access status, and available abstracts. Enter
`BEFORE 1989 words` to restrict results to literature published before 1989. Academic
results use `OA` record identifiers and share the live cache, marking, and download
features. Casual searches work without a key; setting `OPENALEX_API_KEY` raises the
OpenAlex usage allowance.

---

[Back to the user guide](../USER_GUIDE.md)
