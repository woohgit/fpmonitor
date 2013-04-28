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

Scenario: ALl nodes have different status
    Given I am logged in
    When I have 5 different nodes with different status
    Then I should see 5 different status