Feature: Login

Scenario: I can log in
    Given I am not logged in
    When I log in
    Then I should be logged in

Scenario: I can log out
    Given I am logged in
    When I log out
    Then I should be logged out

Scenario: I cannot log in with invalid credentials
    Given I am logged out
    When I login with bad credentials
    Then I should be on the login page with a "Invalid login credentials!" message

Scenario: I cannot login with an inactive user
    Given I am logged out
    When I login with an inactive user
    Then I should be on the login page with a "Inactive account!" message