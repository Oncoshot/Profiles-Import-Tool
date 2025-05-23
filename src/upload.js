const https = require('https');
const fs = require('fs')

const { authenticate } = require('./auth.js');
const organizationId = process.env.ONCOSHOT_ORGANISATION
const API_HOSTNAME = process.env.API_HOSTNAME

// use it, to re-upload specific items
const onlyProfilesIds = []

function retrieveFile(inputFileName) {
    let read = fs.readFileSync(inputFileName)
    const results = JSON.parse(read)
    return results
}

function uploadProfiles(profiles, command) {
    let token = null;
    authenticate().then(async (initialToken) => {
        
        if (!initialToken) throw new Error("Authentication Failure")

        token = initialToken;
        console.log("Authentication Successful")

        let log = ""
        let successCount = 0
        let failureCount = 0

        if (onlyProfilesIds.length) {
            profiles = profiles.filter(item => onlyProfilesIds.includes(item.id))
        }

        // Push each entry
        for (let i = 0; i < profiles.length; i++) {
            const profile = profiles[i]
            const id = profile.id || profile.Id
            const data = JSON.stringify(profile)

            // Define request function with 401 reauth + retry
            const sendRequest = (retry = false) => {
                return new Promise((resolve, reject) => {
                    
                    const options = {
                        hostname: API_HOSTNAME,
                        path: `/api/v1/organizations/${organizationId}/profiles/${id}/${command}`,
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'authorization': `Bearer ${token}`
                        }
                    }

                    const req = https.request(options, res => {
                        console.log(`${i} Profile ${id}: statusCode: ${res.statusCode}${retry ? ' (retry)' : ''}`)
                        log += `${i} Profile ${id}: statusCode: ${res.statusCode}${retry ? ' (retry)' : ''}\n`

                        let responseBody = ""
                        res.on("data", chunk => {
                            responseBody += chunk;
                            if (res.statusCode === 422) {
                                log += chunk + '\n'
                                fs.writeFile(`./logs/${id}_failure-profile.json`, data, "utf8", err => {
                                    if (err) console.log(err)
                                })
                            }
                        });

                        res.on("end", async () => {
                            if ([201, 204].includes(res.statusCode)) {
                                successCount++;
                                resolve();
                            } else if (res.statusCode === 401 && !retry) {
                                console.log(`401 for profile ${id}. Reauthenticating...`);
                                try {
                                    token = await authenticate(); // get new token
                                    console.log("Reauthentication successful. Retrying...");
                                    await sendRequest(true); // retry same profile
                                    resolve();
                                } catch (authErr) {
                                    console.error("Reauthentication failed:", authErr);
                                    failureCount++;
                                    resolve();
                                }
                            } else {
                                failureCount++;
                                resolve();
                            }
                        });
                    });

                    req.on("error", error => {
                        console.error(error);
                        log += error + "\n";
                        failureCount++;
                        resolve();
                    });

                    req.write(data);
                    req.end();
                });
            };

            await sendRequest();
        }

        console.log(`\nUpload complete \nSuccessful: ${successCount} \nFailed: ${failureCount}`);
        log += `Upload complete \nSuccessful: ${successCount} \nFailed: ${failureCount}\n`;

        fs.writeFile(`./logs/${Date.now()}-upload-log.txt`, log, "utf8", err => {
            if (err) console.log(err);
        });
    }).catch(err => {
        console.error("Authentication Failure:", err);
        throw new Error("Authentication Failure");
    })
}

console.log("This tool uploads the formatted JSON file to the Oncoshot API.\n")
console.log("Guide to statusCodes:")
console.log("201: Success, created new profile")
console.log("204: Success, updated existing profile")
console.log("401: Failure, authentication failed")
console.log("403: Failure, no access to organisation")
console.log("422: Failure, data is wrongly formatted\n")

if (!process.argv[2]) {
    throw new Error("No file input")
}
let inputFileName = process.argv[2]

if (!process.argv[3]) {
    throw new Error("No command input")
}
let command = process.argv[3]

if (command !== 'import' && command !== 'merge') {
    throw new Error("Wrong command: " + command)
}

try {
    profiles = retrieveFile(inputFileName)
    console.log(`Profiles to upload : ${profiles.length}`)
    uploadProfiles(profiles, command)
} catch (err) {
    if (err.code === "ENOENT") {
        console.error(inputFileName + " is not valid JSON file location")
    } else {
        console.error(err)
    }
}    

