import { By, Key, until } from 'selenium-webdriver';
import { driver, markers, test } from 'thousandeyes';

runScript();

async function runScript() {
    const settings = test.getSettings();

    // Load the target URL
    markers.start('LoadPage');
    await driver.get(settings.url);
    await driver.takeScreenshot();
    markers.stop('LoadPage');

    // Fetch the raw JSON response directly
    markers.start('FetchJSON');
    const jsonResponse = await driver.executeScript('return document.body.innerText');
    markers.stop('FetchJSON');
    await driver.takeScreenshot();

    // Parse the JSON response
    let data;
    try {
        data = JSON.parse(jsonResponse);
    } catch (e) {
        test.fail('Failed to parse JSON response: ' + e.message);
        return; // Exit the script on parsing failure
    }

    // Components to check
    const components = ['database', 'cyberark', 'infoblox', 'Redis'];

    // Validate the status of each component
    markers.start('ValidateComponents');
    let failedComponents = [];
    for (const component of components) {
        if (data[component] !== 'working') {
            failedComponents.push(component);
        }
    }
    markers.stop('ValidateComponents');

    // Log and assert results
    if (failedComponents.length > 0) {
        test.fail('The following components are not working: ' + failedComponents.join(', '));
    } else {
        test.log('All components are working as expected.');
    }

    // End of script
    await driver.takeScreenshot();
}
