Given(/^I am on the a node page$/) do
    log_in
    visit 'http://192.168.56.1:8000/test_api/create_nodes/1/1'
    visit 'http://192.168.56.1:8000/index'
    my_link = page.all(:xpath, "//a[contains(@href,'node/')]")[0]
    my_link.click
end

When(/^I add a new email address "(.*?)"$/) do |email|
    fill_in "address", :with => email
    click_button("Add")
end

Then(/^I should see the new email address "(.*?)"$/) do |email|
    page.should have_content(email)
end

When(/^When I delete the address "(.*?)"$/) do |email|
    to_delete_email = email.sub! '@', '_'
    my_link = find_by_id(to_delete_email)
    my_link.click
    page.all("#dataConfirmModal").count.should == 1
    click_link "OK"
end

Then(/^I should not see the email address "(.*?)"$/) do |email|
    page.should_not have_content(email)
end