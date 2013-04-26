Feature: Login

Scenario:
    Given I am not logged in
    When I log in
    Then I should be logged in

Scenario:
    Given I am logged in
    When I log out
    Then I should be logged out

Scenario:
    Given I am logged out
    When I login with bad credentials
    Then I should be on the login page with a "Invalid login credentials!" message

Scenario:
    Given I am logged out
    When I login with an inactive user
    Then I should be on the login page with a "Inactive account!" message