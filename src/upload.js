const https = require('https');
const fs = require('fs')

const { authenticate } = require('./auth.js');
const organizationId = process.env.ONCOSHOT_ORGANISATION
const API_HOSTNAME = process.env.API_HOSTNAME

// use it, to re-upload specific items
const onlyProfilesIds = []

function retrieveFile(inputFileName) {
    let read = fs.readFileSync(inputFileName)
    results = JSON.parse(read)
    return results
}


function uploadProfiles(profiles, command) {
    authenticate().then(async (token, err) => {
        let log = ""
        if (!token || err) {
            throw new Error('Authentication Failure')
        }

        console.log("Authentication Successful")


        let successCount = 0
        let failureCount = 0

        if (onlyProfilesIds.length) {
          profiles = profiles.filter(item => onlyProfilesIds.includes(item.id))
        }

        // Push each entry
        for (let i = 0; i < profiles.length; i++) {
            await new Promise(async (resolve, reject) => {
                // Set id
                const id = profiles[i].id || profiles[i].Id

                const data = JSON.stringify(profiles[i])

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
                    log += `${i} Profile ${id}: statusCode: ${res.statusCode}\n`
                    console.log(`${i} Profile ${id}: statusCode: ${res.statusCode}`)

                    res.on("data", function(chunk) {
                      if (res.statusCode === 422) {
                        log += chunk + '\n'
                        fs.writeFile(`./logs/${id}_failure-profile.json`, data, "utf8", (res, err) => {
                          if (err) {
                            console.log(err)
                          }
                        })
                      }
                    });

                    if ([201, 204].includes(res.statusCode)) {
                        successCount++;
                    } else {
                        failureCount++;
                    }
                    resolve()
                })

                req.on('error', error => {
                    console.error(error)
                    log += error + '\n'
                    reject(err)
                })

                req.on('end', () => {
                    console.log(`${id} upload complete`)
                })

                req.write(data)
                req.end()
            })
        }

        console.log(`\nUpload complete \nSuccessful: ${successCount} \nFailed: ${failureCount}`)

        log += `Upload complete \nSuccessful: ${successCount} \nFailed: ${failureCount}\n`

        // Write Log to file
        fs.writeFile(`./logs/${Date.now()}-upload-log.txt`, log, "utf8", (res, err) => {
            if (err) {
                console.log(err)
            }
        })
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

if(command!='import' && command!='merge') {
    throw new Error("Wrong command: " + command)
}

try {
    profiles = retrieveFile(inputFileName)
    console.log(`Profiles to upload : ${profiles.length}`)
    
    uploadProfiles(profiles, command)
} catch (err) {
    if (err.code == "ENOENT") {
        console.error(inputFileName + " is not valid json file location")
        return
    } else {
        console.error(err)
        return
    }
}    

