import React from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box, Typography } from '@mui/material';
import WaitlistForm from './components/WaitlistForm';
import { styled } from "@mui/system";

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
        <GradientText variant="h2" paddingTop={10} sx={{ fontSize: { md: '6rem', xs: '3rem' }, fontWeight: 'bold' }}>
          Token Telescope
        </GradientText>
        <WaitlistForm />
        
      </Box>
    </ThemeProvider>
  );
}

export default App;
