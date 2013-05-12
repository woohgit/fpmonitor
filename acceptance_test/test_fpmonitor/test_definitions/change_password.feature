Feature: Change password

Scenario: I change my password
    Given I am logged in
    And I click on the "Change password" menupoint
    When I fill the form properly with "admin" "newadmin" "newadmin"
    Then I should be redirected to the index page

Scenario: I change back my password
    Given I am logged in with "admin" "newadmin"
    And I click on the "Change password" menupoint
    When I fill the form properly with "newadmin" "admin" "admin"
    Then I should be redirected to the index page