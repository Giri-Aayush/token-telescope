const express = require("express");
const app = express();
// This is your test secret API key.

app.use(express.static("public"));
app.use(express.json());



app.listen(4242, () => console.log("Node server listening on port 4242!"));