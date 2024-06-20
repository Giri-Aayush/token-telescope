require('dotenv').config();
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const supabase = require('./supabaseClient');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 5000;
const JWT_SECRET = process.env.JWT_SECRET;

// Middleware to protect routes
const authMiddleware = async (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  if (!token) return res.status(401).send('Access Denied');

  try {
    const verified = jwt.verify(token, JWT_SECRET);
    req.user = verified;
    next();
  } catch (err) {
    res.status(400).send('Invalid Token');
  }
};
//This is a test Comment


// Register
app.post('/api/register', async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) return res.status(400).send('Email and password are required');

  const { data: userExists } = await supabase
    .from('users')
    .select('*')
    .eq('email', email)
    .single();

  if (userExists) return res.status(400).send('Email already exists');

  const salt = await bcrypt.genSalt(10);
  const hashedPassword = await bcrypt.hash(password, salt);

  const { data, error } = await supabase
    .from('users')
    .insert([{ email, password: hashedPassword, usage_count: 0, plan: 'none' }]);

  if (error) return res.status(400).send('Error registering user');

  res.send('User registered successfully');
});

// Login
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) return res.status(400).send('Email and password are required');

  const { data: user, error } = await supabase
    .from('users')
    .select('*')
    .eq('email', email)
    .single();

  if (error || !user) return res.status(400).send('Invalid email or password');

  const validPass = await bcrypt.compare(password, user.password);
  if (!validPass) return res.status(400).send('Invalid email or password');

  const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET);
  res.header('Authorization', 'Bearer ' + token).send({ token, user });
});

// Get user info (protected route)
app.get('/api/user', authMiddleware, async (req, res) => {
  const { data: user, error } = await supabase
    .from('users')
    .select('id, email, usage_count, plan')
    .eq('id', req.user.id)
    .single();

  if (error) return res.status(400).send('User not found');

  res.send(user);
});

// Increment usage count (protected route)
app.post('/api/use-service', authMiddleware, async (req, res) => {
  const { data: user, error } = await supabase
    .from('users')
    .select('*')
    .eq('id', req.user.id)
    .single();

  if (error) return res.status(400).send('User not found');

  if (user.plan !== 'lifetime' && user.usage_count <= 0) {
    return res.status(400).send('No usage left, please purchase more');
  }

  const newUsageCount = user.plan === 'lifetime' ? user.usage_count : user.usage_count - 1;

  const { error: updateError } = await supabase
    .from('users')
    .update({ usage_count: newUsageCount })
    .eq('id', req.user.id);

  if (updateError) return res.status(400).send('Error updating usage count');

  res.send('Service used, remaining count: ' + newUsageCount);
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
