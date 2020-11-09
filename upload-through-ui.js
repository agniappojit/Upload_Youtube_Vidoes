const fs = require('fs');

const addExitCallback = require('catch-exit').addExitCallback;
const puppeteer = require('puppeteer');

const userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36";

const { Command } = require('commander');
const { exit } = require('process');
const program = new Command();
program.version('0.0.1');

program
    .option('--channel-id <id>', 'YouTube channel ID')
    .option('--cookies-file <path>', 'path to the browser cookies file to be logged in in JSON format')
    .option('--video-file <path>', 'local path to the video file to be uploaded');

addExitCallback((exitCode) => {
    if (exitCode !== 1) {
        return;
    }

    console.log();
    program.outputHelp();
});


try {
    program.parse(process.argv);
} catch (err) {
    exit(1);
}
shouldExit = false;

if (!program.channelId) {
    console.warn('YouTube channel ID needs to be provided');
    shouldExit = true;
}

if (!program.cookiesFile) {
    console.warn('Cookies JSON file needs to be provided');
    shouldExit = true;
}

if (!program.videoFile) {
    console.warn('Video file path needs to be provided');
    shouldExit = true;
}

if (shouldExit) {
    exit(1);
}

function pathExistsOrWarn(path) {
    if (fs.existsSync(path)) {
        return true;
    }

    console.warn(path + ' does not exist.');
    console.warn('Please provide a correct path.');
    return false;
}

if (!pathExistsOrWarn(program.cookiesFile)) {
    shouldExit = true;
}
if (!pathExistsOrWarn(program.videoFile)) {
    shouldExit = true;
}
if (shouldExit) {
    exit(1);
}

// exit();

function isInt(value) {
    var x;
    if (isNaN(value)) {
        return false;
    }
    x = parseFloat(value);
    return (x | 0) === x;
}

(async () => {
    let browser;
    try {
        console.log("Opening the browser...");
        browser = await puppeteer.launch({
            // headless: false,
            args: [
                "--disable-setuid-sandbox",
                // '--start-maximized'
            ],
            'ignoreHTTPSErrors': true,
            executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        });
    } catch (err) {
        console.log("Could not create a browser instance => : ", err);
    }

    const page = await browser.newPage();
    // await page.setViewport({ width: 1366, height: 768 });
    await page.setUserAgent(userAgent);

    // './studio.youtube.com.cookies.json'
    // console.log("Reading cookies file......");
    const cookiesString = fs.readFileSync(program.cookiesFile);
    const cookies = JSON.parse(cookiesString);
    console.log("Setting cookies...");
    await page.setCookie(...cookies);

    // NPedia User Channel
    // UCJoZcIAkUodPyA95oOF-ucQ
    // Priyesha YT
    // UCo6ncI0ONM6qE4i-GtFYGhA



    try {
        process.stdout.write("Loading YouTube upload page...");
        uploadPageUrl = 'https://studio.youtube.com/channel/' + program.channelId + '/videos/upload?d=ud';
        // console.log(uploadPageUrl);
        await page.goto(uploadPageUrl, {
            waitUntil: 'networkidle0'
        });
        console.log('[DONE]');
    } catch (e) {
        console.log('[KO]');
        console.log(e);
        await browser.close();
        return;
    }


    try {
        process.stdout.write('Waiting for HTML file input to be available... ');
        await page.waitForSelector('input[type=file]');
        console.log('[DONE]');
    }
    catch (e) {
        console.log('Timeout exceeded.');
        await browser.close();
        return;
    }

    await page.waitForTimeout(1000);

    const inputUploadHandle = await page.$('input[type=file]');
    // './videos/10000-year-old-book-part-3-shiva-sutras-13-jul-2006.mp4';
    let fileToUpload = program.videoFile;
    // Sets the value of the file input to fileToUpload
    // console.log("Setting the value of the file input......");
    inputUploadHandle.uploadFile(fileToUpload);

    // doing click on button to trigger upload file
    await page.waitForSelector('#select-files-button');
    console.log("Uploading file...");
    await page.evaluate(() => document.getElementById('select-files-button').click());

    // Wait for Upload progress message to appear on bottom left of upload popup
    await page.waitForSelector('span.ytcp-video-upload-progress');

    // Wait for "Finished processing" message to know that upload is complete
    let isUploadComplete = false;

    const ProgressBar = require('progress');
    const bar = new ProgressBar('[:bar] :percent', {
        complete: '=',
        incomplete: ' ',
        width: 20,
        total: 100
    });

    let prevUploadPercent = 0;

    while (!isUploadComplete) {
        uploadProgressMessage = await page.evaluate(
            element => element.textContent,
            await page.$('span.ytcp-video-upload-progress')
        );

        // When upload completed, "XX% processed" message appears
        isUploadComplete = uploadProgressMessage.includes('processed');
        if (!isUploadComplete && uploadProgressMessage.includes('uploaded')) {
            // console.log(uploadProgressMessage);
            uploadPercent = uploadProgressMessage.trim().substring(0, 2).replace('%', '');

            if (uploadPercent != prevUploadPercent && isInt(uploadPercent)) {

                bar.tick(uploadPercent);
                prevUploadPercent = uploadPercent;
                console.log("uploadPercent");
                console.log(uploadPercent);
                console.log("prevUploadPercent");
                console.log(prevUploadPercent);
            }
        }

        await page.waitForTimeout(2000);
    }
    console.log('\n');
    console.log('[DONE]');

    const youtubeVideoLink = await page.evaluate(element => element.textContent, await page.$('a.ytcp-video-info'));
    console.log();
    console.log('Link to uploaded video:');
    // Needs to be printed on a separate line to be retrieved by a calling program
    console.log(youtubeVideoLink.trim());

    await browser.close();
})();
