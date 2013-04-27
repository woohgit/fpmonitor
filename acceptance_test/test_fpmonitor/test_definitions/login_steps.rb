After do |scenario|
    if(scenario.failed?)
        page.driver.browser.save_screenshot("reports/#{scenario.name}.png")
        embed("#{scenario.name}.png", "image/png", "SCREENSHOT")
    end
end

Given /^I am not logged in$/ do
    log_out
end

When /^I log in$/ do
    fill_in "username", :with => "admin"
    fill_in "password", :with => "admin"
    click_button("signin")
end

Then /^I should be logged in$/ do
    page.should have_content("Logged in")
end

Given /^I am logged in$/ do
    log_in
end

When /^I log out$/ do
    log_out
end

Then /^I should be logged out$/ do
    page.should have_content("K\u00E9rlek l\u00E9pj be!")
end

Given /^I am logged out$/ do
    log_out
end

When /^I login with bad credentials$/ do
    fill_in "username", :with => "admin"
    fill_in "password", :with => "wrong_password"
    click_button("signin")
end

Then /^I should be on the login page with a "(.*?)" message$/ do |message|
    page.should have_content(message)
end

When /^I login with an inactive user$/ do
    fill_in "username", :with => "inactive_admin"
    fill_in "password", :with => "admin"
    click_button("signin")
end


def log_in
    visit "http://192.168.56.1:8000/login"
    fill_in "username", :with => "admin"
    fill_in "password", :with => "admin"
    click_button("signin")
end

def log_out
    visit 'http://192.168.56.1:8000/logout'
end
