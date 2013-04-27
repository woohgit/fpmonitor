After do |scenario|
    if(scenario.failed?)
        page.driver.browser.save_screenshot("reports/#{scenario.name}.png")
        embed("#{scenario.name}.png", "image/png", "SCREENSHOT")
    end
    visit 'http://192.168.56.1:8000/test_api/cleanup_nodes'
end
