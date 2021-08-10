const request = require("request");

async function authenticate() {
    return new Promise(res => {
        var options = {
            method: 'POST',
            url: 'https://auth.oncodevel.com/oauth/token',
            headers: { 'content-type': 'application/json' },
            body: `{"client_id":"${process.env.AUTH0_CLIENT_ID}","client_secret":"${process.env.AUTH0_CLIENT_SECRET}","audience":"${process.env.AUTH0_DOMAIN}","grant_type":"client_credentials"}`
        }
        request(options, function (error, response, body) {
            if (error) throw new Error(error);
            res(JSON.parse(body).access_token)
        });


    })
}
// auth().then((res, err) => {
//     console.log(res)
// })

exports.authenticate = authenticate;