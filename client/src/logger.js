/* read more about winston: https://www.npmjs.com/package/winston */

'use strict';

const winston = require('winston');

module.exports = new (winston.Logger)({
    transports: [
        new (winston.transports.Console)({
            colorize: true,
            timestamp: true,
            stringify: true,
            prettyPrint: true
        }),
        new (winston.transports.File)({
            timestamp: true,
            stringify: true,
            filename: "log"
        })
    ]
});
