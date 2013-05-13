When(/^I have (.+) nodes$/) do |count|
    visit 'http://192.168.56.1:8000/test_api/cleanup_nodes'
    visit 'http://192.168.56.1:8000/test_api/create_nodes/' + count.to_s() + '/0'
    page.should have_content("OK")
end

Then(/^I should see (\d+) nodes$/) do |count|
    visit 'http://192.168.56.1:8000/index'
    if count.to_i() == 0
        num_to_check = 0
    else
        num_to_check = count.to_i() + 1
    end
    page.all('table#node_list tr').count.should == num_to_check
end

Then(/^I should see (\d+) "(.*?)" nodes$/) do |count, status|
    if status == "OK"
        style = "success"
    end
    if status == "ERROR"
        style = "important"
    end
    visit 'http://192.168.56.1:8000/index'
    page.all('span.label-' + style).count.should == count.to_i()
end

When(/^I have (\d+) nodes with status "(.*?)"$/) do |count, status|
    if status == "OK"
        status_code = 0
    end
    if status == "ERROR"
        status_code = 4
    end
    visit 'http://192.168.56.1:8000/test_api/create_nodes/' + count.to_s() + '/' + status_code.to_s()
end

When(/^I have (\d+) different nodes with different status$/) do |count|
    i = 0
    while i < count.to_i()
        name = 'nodename' + i.to_s()
        visit 'http://192.168.56.1:8000/test_api/create_nodes/1/' + i.to_s() + '/' + name
        i+=1
    end
end

Then(/^I should see (\d+) different status$/) do |count|
    visit 'http://192.168.56.1:8000/index'
    page.all('span.label-success').count.should == 1
    page.all('span.label-info').count.should == 1
    page.all('span.label-warning').count.should == 2    # because we have a warning label
    page.all('span.label-important').count.should == 1
    page.all('span.label-').count.should == 1
end

When(/^I set the first node to maintenance mode$/) do
    visit 'http://192.168.56.1:8000/index'
    first('.switch-left').click
end

Then(/^I should see the first node is in maintenance mode after reloading$/) do
    visit 'http://192.168.56.1:8000/index'
    page.all('.switch-off').count.should == 1
    page.all('.switch-on').count.should == 2
end


Then(/^I should see a warning message "(.*?)"$/) do |message|
    visit 'http://192.168.56.1:8000/index'
    page.should have_content(message)
end

When(/^I disable the test mode$/) do
    visit 'http://192.168.56.1:8000/test_api/test_mode_off'
    page.should have_content("OK")
end

Then(/^I should not see a warning message "(.*?)"$/) do |message|
    visit 'http://192.168.56.1:8000/index'
    page.should_not have_content(message)
    visit 'http://192.168.56.1:8000/test_api/test_mode_on'
end

When(/^I try to delete node (\d+)$/) do |id|
    visit 'http://192.168.56.1:8000/index'
    index = id.to_i() - 1
    my_link = page.all(:xpath, "//a[contains(@href,'delete_node/')]")[index]
    my_link.click
end

Then(/^I should see a popup confirmation window$/) do
    page.all("#dataConfirmModal").count.should == 1
end

When(/^I select the "(.*?)" button$/) do |button|
    click_button button
end