Feature: Notification Addresses

Scenario: I can add a new address to a node
    Given I am on the a node page
    When I add a new email address "newemail@wooh.hu"
    Then I should see the new email address "newemail@wooh.hu"

Scenario: I can delete an address
    Given I am on the a node page
    And I add a new email address "newemail@wooh.hu"
    When When I delete the address "newemail@wooh.hu"
    Then I should not see the email address "newemail@wooh.hu"