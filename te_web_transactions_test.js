import { By, Key, until } from 'selenium-webdriver';
import { driver, markers, test } from 'thousandeyes';

runScript();

async function runScript() {
    const settings = test.getSettings();

    // Load the target page
    markers.start('LoadPage');
    await driver.get(settings.url);
    await driver.takeScreenshot();
    markers.stop('LoadPage');

    // Wait for the page to load and get the response body
    markers.start('FetchJSON');
    const responseElement = await driver.findElement(By.tagName('body')); // Assuming response is in the body tag
    const jsonResponse = await responseElement.getText();
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
