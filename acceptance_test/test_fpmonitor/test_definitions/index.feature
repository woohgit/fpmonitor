Feature: Index

Scenario: I see my nodes
    Given I am logged in
    When I have 5 nodes
    Then I should see 6 nodes