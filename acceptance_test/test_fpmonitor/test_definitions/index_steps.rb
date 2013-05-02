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
        style = "danger"
    end
    visit 'http://192.168.56.1:8000/index'
    page.all('button.btn-' + style).count.should == count.to_i()
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
    page.all('button.btn-success').count.should == 1
    page.all('button.btn-info').count.should == 1
    page.all('button.btn-warning').count.should == 1
    page.all('button.btn-danger').count.should == 1
    page.all('button.btn-').count.should == 1
end

When(/^I set the first node to maintenance mode$/) do
    visit 'http://192.168.56.1:8000/index'
    first('.switch-left').click
end

When(/^I reload the index page$/) do
    visit 'http://192.168.56.1:8000/'
end

Then(/^I should see the first node is in maintenance mode$/) do
    cb = all("input[type='checkbox']")[0]
    cb.should_not be_checked
end