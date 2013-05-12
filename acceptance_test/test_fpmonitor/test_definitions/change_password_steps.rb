Given(/^I click on the "(.*?)" menupoint$/) do |link|
    click_link link
end

When(/^I fill the form properly with "(.*?)" "(.*?)" "(.*?)"$/) do |pass,pass2,repass2|
    fill_in "id_old_password", :with => pass
    fill_in "id_new_password1", :with => pass2
    fill_in "id_new_password2", :with => repass2
    click_button("Change my passwor")
end

Then(/^I should be redirected to the index page$/) do
    current_path.should == "/index"
end

Given (/^I am logged in with "(.*?)" "(.*?)"$/) do |username, password|
    log_out
    visit "http://192.168.56.1:8000/login"
    fill_in "username", :with => username
    fill_in "password", :with => password
    click_button("signin")
end