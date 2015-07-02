Feature: Homepage
    A listing of entries from the learning journal in reverse
    chronological order

Scenario: The Homepage lists entries for anonymous users
    Given an anonymous user
    And a list of 3 entries
    When the user vists the homepage
    Then they see a list of 3 entries

Feature: Markdown
    Given an author
    When the user adds an entry
    Then that entry fomats with markdown

Feature: Colorized Code
    Given an author
    When the user adds code in an entry
    Then that entry shows color in the code
