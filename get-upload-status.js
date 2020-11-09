const fs = require('fs');

const addExitCallback = require('catch-exit').addExitCallback;
const puppeteer = require('puppeteer');

const userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36";

const { Command } = require('commander');
const { exit } = require('process');
const program = new Command();
program.version('0.0.1');

program
    .option('--cookies-file <path>', 'path to the browser cookies file to be logged in in JSON format')
    .option('--video-id <id>', 'YouTube video ID')


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

if (!program.cookiesFile) {
    console.warn('Cookies JSON file needs to be provided');
    shouldExit = true;
}

if (!program.videoId) {
    console.warn('YouTube video ID needs to be provided');
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

if (shouldExit) {
    exit(1);
}

// exit();

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
    process.stdout.write("Setting cookies... ");
    await page.setCookie(...cookies);
    console.log('[DONE]');


    trialCounts = 2;

    process.stdout.write("Loading YouTube video edit page... ");
    detailsPageUrl = 'https://studio.youtube.com/video/' + program.videoId + '/edit/basic';
    // console.log(detailsPageUrl)

    await page.goto(detailsPageUrl, {
        waitUntil: 'networkidle0'
    });
    console.log('[DONE]');


    try {
        process.stdout.write('Waiting for HTML element containing video status... ');
        await page.waitForSelector('.uploading-overlay');
        console.log('[DONE]');
    }
    catch (e) {
        console.log('Timeout exceeded.');

        process.stdout.write('Loading YouTube video page... ');
        await page.goto('https://www.youtube.com/watch?v=' + program.videoId, {
            waitUntil: 'networkidle0'
        });
        console.log('[DONE]');

        // 2020-10-05
        // Reason messages:
        // - We're processing this video. Check back later.
        // - Video unavailable
        //      Subreason messages:
        //      - This video has been removed by the uploader

        console.log('Video status:');
        await page.waitForSelector('#reason');
        let reason = await page.evaluate(element => element.textContent, await page.$('#reason'));
        reason = reason.trim();
        console.log(reason);

        if (reason.includes('unavailable')) {
            await page.waitForSelector('#subreason');
            let subreason = await page.evaluate(element => element.textContent, await page.$('#subreason'));
            subreason = subreason.trim();
            console.log(subreason);

            if (subreason.includes('removed')) {
                console.log('removed');
            } else {
                console.log('unavailable');
            }

            await browser.close();
        } else {
            if (reason.includes('processing')) {
                console.log('processing');
            }
        }

        await browser.close();
        return;
    }

    process.stdout.write('Getting video status... ');
    // 2020-10-04
    // Example texts displayed in <div class="uploading-overlay">...</div>
    // Processing video...
    // Uploading video...
    let videoStatus = await page.evaluate(element => element.textContent, await page.$('.uploading-overlay'));
    console.log('[DONE]');

    // Getting video status "word"
    // "Uploading video..." => "uploading"
    videoStatus = videoStatus.trim().toLowerCase().split(' ')[0];

    console.log('Video status:');
    // Needs to be printed on a separate line to be retrieved by a calling program
    console.log(videoStatus);

    await browser.close();
})();
