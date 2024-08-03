import React, { useState } from 'react';
import { Box, Typography, Button, TextField, Tabs, Tab } from '@mui/material';
import { styled } from '@mui/system';
import { useNavigate } from 'react-router-dom';

const GradientText = styled(Typography)({
  background: 'linear-gradient(to bottom, #cccccc, #666666)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
});

const CustomButton = styled(Button)({
  height: '48px',
  background: 'linear-gradient(110deg, #000103 45%, #1e2631 55%, #000103)',
  backgroundSize: '200% 100%',
  color: '#b3b3b3',
  border: '1px solid #666666',
  marginTop: '24px',
  '&:hover': {
    background: 'linear-gradient(110deg, #1e2631 45%, #000103 55%, #1e2631)',
  },
});

const useStyles = styled((theme) => ({
  authSection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: 'black',
    color: 'white',
    textAlign: 'center',
    padding: theme.spacing(2),
  },
  formContainer: {
    backgroundColor: '#1e1e1e',
    padding: theme.spacing(4),
    borderRadius: '10px',
    boxShadow: '0 3px 5px 2px rgba(30, 136, 229, .3)',
  },
  formField: {
    marginBottom: theme.spacing(2),
    '& .MuiInputBase-input': {
      color: 'white',
    },
    '& .MuiInputLabel-root': {
      color: 'white',
    },
    '& .MuiOutlinedInput-root .MuiOutlinedInput-notchedOutline': {
      borderColor: 'white',
    },
  },
  authButton: {
    height: '48px',
    background: 'linear-gradient(110deg, #000103 45%, #1e2631 55%, #000103)',
    backgroundSize: '200% 100%',
    color: '#b3b3b3',
    border: '1px solid #666666',
    marginTop: theme.spacing(3),
    '&:hover': {
      background: 'linear-gradient(110deg, #1e2631 45%, #000103 55%, #1e2631)',
    },
  },
}));

const LoginPage = () => {
  const classes = useStyles();
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleTabChange = (event, newValue) => {
    setIsLogin(newValue === 0);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const endpoint = isLogin ? '/login' : '/register';
    const response = await fetch(`http://localhost:4000${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    if (response.ok) {
      console.log("API response token", data.token);
      navigate('/predict'); // Navigate to the predict page
    } else {
      alert(`Error: ${data.message}`);
    }
  };

  return (
    <Box className={classes.authSection}>
      <GradientText variant="h1" sx={{ fontSize: { md: '4rem', xs: '2.5rem' }, fontWeight: 'bold' }}>
        Token Telescopy
      </GradientText>
      <Box className={classes.formContainer}>
        <form onSubmit={handleSubmit}>
          <TextField
            className={classes.formField}
            label="Username"
            variant="outlined"
            fullWidth
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            className={classes.formField}
            label="Password"
            variant="outlined"
            type="password"
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <CustomButton
            type="submit"
            className={classes.authButton}
          >
            {isLogin ? 'Login' : 'Sign Up'}
          </CustomButton>
        </form>
      </Box>
    </Box>
  );
};

export default LoginPage;
