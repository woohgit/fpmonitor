Feature: Index

Scenario: I have no nodes
    Given I am logged in
    When I have 0 nodes
    Then I should see 0 nodes

Scenario: I see my nodes
    Given I am logged in
    When I have 3 nodes
    Then I should see 3 nodes

Scenario: All nodes have the status OK
    Given I am logged in
    When I have 3 nodes with status "OK"
    Then I should see 3 "OK" nodes

Scenario: All nodes have the status ERROR
    Given I am logged in
    When I have 3 nodes with status "ERROR"
    Then I should see 3 "ERROR" nodes

Scenario: All nodes have different status
    Given I am logged in
    When I have 5 different nodes with different status
    Then I should see 5 different status

Scenario: I change one of my nodes to maintenance mode
    Given I am logged in
    And I have 3 nodes with status "OK"
    When I set the first node to maintenance mode
    Then I should see the first node is in maintenance mode after reloading

Scenario: I see a warning message when the system is in test mode
    Given I am logged in
    Then I should see a warning message "Warning! The test mode is ON"

Scenario: I should not see a warning message when the system is not in test mode
    Given I am logged in
    When I disable the test mode
    Then I should not see a warning message "Warning! The test mode is ON"

Scenario: Confirmation dialogue pops up when deleting a node
    Given I am logged in
    And I have 3 nodes with status "OK"
    When I try to delete node 1
    Then I should see a popup confirmation window