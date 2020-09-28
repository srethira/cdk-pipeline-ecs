"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
async function handler(event, context) {
    return {
        body: 'Hello from a Lambda Function',
        statusCode: 200,
    };
}
exports.handler = handler;