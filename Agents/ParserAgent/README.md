# Humans Detected Parsers

All Parser Agents are based on the AbstractParser class, or are created by a descendant of the AbstractFactory class.

## Operations

### Order of processing

Parser Agents process recorded texts by primary key in a strictly increasing order:
Agents assume that all texts to process have a higher key than the previous text processed.

Motivation:

- Each Parger Agent must only persist a single integer, the last processed key, rather than a bit for every htext in the database.

Implications:

- If a text is removed from the DB, the associated primary key becomes permanently associated with a null row
- Length must be used to determine the number of texts in the database
