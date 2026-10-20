def find_abbreviation_clause(clauses):
    """
    Find the clause containing 3GPP abbreviations.
    """

    for clause in clauses:

        title = clause["title"].lower()

        if "abbreviation" in title:
            return clause

    return None
def extract_abbreviations(clauses):
    """
    Extract abbreviations from the 3GPP abbreviation clause.
    """

    abbreviation_clause = find_abbreviation_clause(
        clauses
    )

    if abbreviation_clause is None:
        return {}

    abbreviations = {}

    for paragraph in abbreviation_clause["paragraphs"]:

        parts = paragraph.split(
            None,
            1
        )

        if len(parts) != 2:
            continue

        abbreviation = parts[0]
        meaning = parts[1]

        abbreviations[abbreviation] = meaning

    return abbreviations