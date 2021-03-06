const request = require("request");
const AUTH0_URL = process.env.AUTH0_URL

async function authenticate() {
    return new Promise(res => {
        var options = {
            method: 'POST',
            url: AUTH0_URL,
            headers: { 'content-type': 'application/json' },
            body: `{"client_id":"${process.env.AUTH0_CLIENT_ID}","client_secret":"${process.env.AUTH0_CLIENT_SECRET}","audience":"${process.env.AUTH0_DOMAIN}","grant_type":"client_credentials"}`
        }
        request(options, function (error, response, body) {
            if (error || JSON.parse(body).error) {
                console.log("Error: " + error)
                throw new Error("Authentication Failed");
            }
            res(JSON.parse(body).access_token)
        });


    })
}
// auth().then((res, err) => {
//     console.log(res)
// })

exports.authenticate = authenticate;