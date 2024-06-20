import React from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box, Typography } from '@mui/material';
import WaitlistForm from './components/WaitlistForm';
import { styled } from "@mui/system";
import HeroSection from './components/Hero';
const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#000000',
    },
    text: {
      primary: '#ffffff',
    },
  },
  typography: {
    fontFamily: 'YourFontFamily', // Make sure to set your font family if it's custom
  },
});

function App() {
  const GradientText = styled(Typography)({
    background: "linear-gradient(to bottom, #cccccc, #666666)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  });
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'background.default',
          textAlign: 'center',
        }}
      >
        <HeroSection />
        <WaitlistForm />
      </Box>
    </ThemeProvider>
  );
}

export default App;
