const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
  },
  password: {
    type: String,
    required: true,
  },
  usageCount: {
    type: Number,
    default: 0,
  },
  plan: {
    type: String,
    default: 'none', // can be 'none', '10_uses', '30_uses', 'lifetime'
  },
});

module.exports = mongoose.model('User', UserSchema);
