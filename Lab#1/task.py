def checkApplciation(score, documents, projects, days):
    problems = []

    if score < 70:
        problems.append("Score is below 70")

    if not documents:
        problems.append("Docments are missing")

    if projects < 70:
        problems.append("Not enough academic projects")
    if days > 7:
        problems.append("Application was submitted late")

    if len(problems) == 0:
        return "Review", "All requirements met"

    return "Hold", ", ".join(problems)


applications = [
    ("Student A", 85, True, 3, 4, "Review"),
    ("Student B", 90, True, 1, 3, "Hold"),
    ("Student C", 78, True, 4, 9, "Hold"),
    ("Student D", 70, True, 2, 7, "Review"),
]

for name, score, documents, projects, days, expected in applications:
    actual, reason = checkApplciation(score, documents, projects, days)

    print("\nApplicant: ", name)
    print("Input: ", score, documents, projects, days)
    print("Expected: ", expected)
    print("Actual: ", actual)
    print("reason: ", reason)
    print("Test passed: ", expected == actual)