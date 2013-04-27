After do |scenario|
    if(scenario.failed?)
        page.driver.browser.save_screenshot("reports/#{scenario.__id__}.png")
        embed("#{scenario.__id__}.png", "image/png", "SCREENSHOT")
    end
    visit 'http://192.168.56.1:8000/test_api/cleanup_nodes'
end

When(/^I create have (.+) nodes$/) do |count|
    visit 'http://192.168.56.1:8000/test_api/cleanup_nodes'
    visit 'http://192.168.56.1:8000/test_api/create_nodes/' + count.to_s() + '/'
    page.should have_content("OK")
end

Then(/^I should see (.+) nodes$/) do |count|
    visit 'http://192.168.56.1:8000/index'
    page.all('table#node_list tr').count.should == count.to_i()+1
end
