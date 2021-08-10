const https = require('https');
const fs = require('fs')

const { authenticate } = require('./auth.js');
const organizationId = process.env.ONCOSHOT_ORGANISATION

let results;

function retrieveFile() {
    try {
        if (!process.argv[2]) {
            throw new Error("No file input")
        }
        let read = fs.readFileSync(process.argv[2])
        results = JSON.parse(read)
        console.log(`Profiles to upload : ${results.length}`)
        uploadProfiles()
    } catch (err) {
        if (err.code == "ENOENT") {
            console.error(process.argv[2] + " is not valid json file location")
            return
        } else {
            console.error(err)
            return
        }
    }
}


function uploadProfiles() {
    authenticate().then(async (token, err) => {
        let log = ""
        if (token == '' || err) {
            throw new Error('Authentication Failure')
        }

        console.log("Authentication Successful")


        let successCount = 0
        let failureCount = 0


        // Push each entry
        for (let i = 0; i < results.length; i++) {
            await new Promise(async (resolve, reject) => {
                // Set id
                const id = results[i].id
                delete results[i]['id']

                const data = JSON.stringify(results[i])

                const options = {
                    hostname: 'api.oncodevel.com',
                    path: `/api/v1/organizations/${organizationId}/profiles/${id}/import`,
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json-patch+json',
                        'Content-Length': data.length,
                        'authorization': `Bearer ${token}`
                    }
                }

                const req = https.request(options, res => {
                    log += `Profile ${id}: statusCode: ${res.statusCode}\n`
                    console.log(`Profile ${id}: statusCode: ${res.statusCode}`)

                    if ([201, 204].includes(res.statusCode)) {
                        successCount++;
                    } else {
                        failureCount++;
                    }
                    resolve()
                    // res.on('data', d => {
                    //     response += d
                    // })
                })

                req.on('error', error => {
                    console.error(error)
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
retrieveFile()
