const express = require("express");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const axios = require("axios");
const cors = require("cors");
const app = express();
app.use(bodyParser.json());
app.use(cors());
const PORT = process.env.PORT || 4000;
const JWT_SECRET = "your_jwt_secret";

// MongoDB connection
mongoose.connect(
  "mongodb+srv://ajstylesmb:O91svz4J7Od2NM2A@accounts.eixze7u.mongodb.net/",
  {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  }
);

// User Schema
const userSchema = new mongoose.Schema({
  username: { type: String, unique: true },
  password: String,
  apiCallCount: { type: Number, default: 0 },
});

const User = mongoose.model("User", userSchema);

// Middleware to authenticate JWT token
const authenticateJWT = (req, res, next) => {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(" ")[1]
  if (token) {
    console.log(JWT_SECRET);
    console.log(token);
    jwt.verify(token, JWT_SECRET, (err, user) => {
      if (err) {
        console.log("JWT verification failed:", err);
        return res.sendStatus(403);
      }
      req.user = user;
      next();
    });
  } else {
    console.log("Authorization header not found");
    res.sendStatus(401);
  }
};

// Check the health of the Server
app.get("/", async (req, res) => {
  console.log("The API is working fine");
  res.status(200).send("The API is working just fine");
});

// Registration endpoint
app.post("/register", async (req, res) => {
  console.log("Entered the Register Endpoint", req.body);
  const { username, password } = req.body;

  // Check for existing username
  const existingUser = await User.findOne({ username });
  if (existingUser) {
    console.log("Username already exists:", username);
    return res.status(400).send("Username already exists");
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const newUser = new User({ username, password: hashedPassword });
  await newUser.save();
  console.log("User registered:", username);
  res.status(201).send("User registered");
});

// Login endpoint
app.post("/login", async (req, res) => {
  console.log("Entered the Login Endpoint", req.body);
  const { username, password } = req.body;
  const user = await User.findOne({ username });
  if (user && (await bcrypt.compare(password, user.password))) {
    const token = jwt.sign({ username: user.username }, JWT_SECRET);
    console.log("Login successful:", username);
    res.json({ token });
  } else {
    console.log("Invalid credentials:", username);
    res.status(401).send("Invalid credentials");
  }
});

// Predict endpoint
app.post("/predict", authenticateJWT, async (req, res) => {
  console.log("Entered the Predict Endpoint", req.body);
  const { contractAddress, nonce } = req.body;
  const user = await User.findOne({ username: req.user.username });
  console.log(req.body);
  // Check if the user has remaining API calls
  console.log(user.apiCallCount)
  if (user.apiCallCount <= 0) {
    console.log("API call limit reached for user:", user.username);
    return res.status(403).send("API call limit reached");
  }

  // Call the Python API
  try {
    console.log("Entered the try of the api for the python call")
    const response = await axios.post("http://127.0.0.1:5000/predict", {
      contractAddress,
      nonce,
    });
    user.apiCallCount -= 1;
    await user.save();
    console.log("API call successful for user:", user.username);
    res.json(response.data);
  } catch (error) {
    console.error("Error calling prediction API:", error);
    res.status(500).send("Error calling prediction API");
  }
});

// Endpoint to increase API call count
app.post("/increase-api-count", authenticateJWT, async (req, res) => {
  console.log("Entered the Increase API Count Endpoint", req.body);
  const { increment } = req.body;
  const user = await User.findOne({ username: req.user.username });

  user.apiCallCount += increment;
  await user.save();
  console.log(
    `Increased API call count for user ${user.username} by ${increment}. New count: ${user.apiCallCount}`
  );
  res
    .status(200)
    .send(
      `API call count increased by ${increment}. New count: ${user.apiCallCount}`
    );
});

// Coinbase webhook endpoint (handle payments)
app.post("/webhook", async (req, res) => {
  console.log("Entered the Webhook Endpoint", req.body);
  // Handle the webhook logic here
  const event = req.body;

  // Example: Update the user's API call count upon successful payment
  if (event.type === "charge:confirmed") {
    const { username } = event.data.metadata; // Assuming username is sent in metadata
    const user = await User.findOne({ username });
    if (user) {
      user.apiCallCount += 100; // Example: Add 100 API calls upon successful payment
      await user.save();
      console.log(
        `Added 100 API calls to user ${username}. New count: ${user.apiCallCount}`
      );
    }
  }

  res.sendStatus(200);
});

app.get('/checkout', async (req, res) => {
  let config = {
    method: 'get',
    maxBodyLength: Infinity,
    url: 'https://api.commerce.coinbase.com/checkouts/a761619b-6995-4480-8f13-4527f3c75792',
    headers: { 
      'Content-Type': 'application/json', 
      'Accept': 'application/json'
    }
  };

  try {
    const response = await axios.request(config);
    res.json(response.data);
  } catch (error) {
    console.error(error);
    res.status(500).send('Error fetching checkout data');
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

const stripe = require("stripe")('sk_test_51OCOZZSCUZeU2No8eYG7r0jOp34053EXy1FXQ77NBUl7w7fRg4Q9CezssKwQ1s5efgSwfCjRxpktMrOGLTP2QMT000VGTB9ccf');

const calculateOrderAmount = (plan) => {
  // Calculate the order total on the server to prevent
  // people from directly manipulating the amount on the client
  let total = 0;
  if (plan == "Basic") {
    total = 10*83*100;
  }
  if(plan == "Standard"){
    total = 20*83*100;
  }
  if(plan == "Lifetime"){
    total = 100*83*100;
  }
  return total;
};

app.post("/create-payment-intent", async (req, res) => {
  const { items } = req.body;
  const amount = calculateOrderAmount(items);

  console.log(amount);
  // Create a PaymentIntent with the order amount and currency
  const paymentIntent = await stripe.paymentIntents.create({
    amount: amount,
    currency: "inr",
    // In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
    automatic_payment_methods: {
      enabled: true,
    },
  });
  console.log(paymentIntent)
  res.send({
    clientSecret: paymentIntent.client_secret,
  });
});
