import React from 'react';
import { Box, Typography, TextField, Button, IconButton } from '@mui/material';
import { styled } from '@mui/system';
import FacebookIcon from '@mui/icons-material/Facebook';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import InstagramIcon from '@mui/icons-material/Instagram';

const GradientText = styled(Typography)({
  background: "linear-gradient(to bottom, #cccccc, #666666)",
  WebkitBackgroundClip: "text",
  WebkitTextFillColor: "transparent",
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
  }
});

const Footer = () => {
  return (
    <Box
      sx={{
        marginX: { lg: 'auto', sm: 10, xs: 7 },
        marginY: 10,
        paddingY: { sm: 16, xs: 8 },
        maxWidth: '910px',
        width: '100%',
        borderRadius: '16px',
        border: '1px solid #666666',
        backgroundColor: 'black',
        position: 'relative',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        textAlign: 'center',
        padding: 4,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          justifyContent: 'center',
        }}
      >
        <GradientText variant="h3" sx={{ fontWeight: 'bold' }}>
          Token Telescope
        </GradientText>
        <Box sx={{ display: 'flex', gap: 2, marginTop: 2 }}>
          <IconButton sx={{ color: '#ffffff' }}>
            <FacebookIcon />
          </IconButton>
          <IconButton sx={{ color: '#ffffff' }}>
            <LinkedInIcon />
          </IconButton>
          <IconButton sx={{ color: '#ffffff' }}>
            <InstagramIcon />
          </IconButton>
        </Box>
      </Box>

      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          justifyContent: 'center',
          maxWidth: '400px',
          width: '100%',
        }}
      >
        <GradientText variant="h4" sx={{ fontWeight: 'bold' }}>
          Contact Us
        </GradientText>
        <TextField
          type="email"
          placeholder="hi@gamil.com"
          variant="outlined"
          sx={{
            marginTop: 2,
            backgroundColor: '#1b1b1b',
            borderColor: '#666666',
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: '#666666',
              },
              '&:hover fieldset': {
                borderColor: '#ffffff',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#00bfa5',
              },
            },
            input: {
              color: '#ffffff',
              padding: '16px',
            },
          }}
          fullWidth
        />
        <TextField
          type="text"
          placeholder="Your message..."
          variant="outlined"
          sx={{
            marginTop: 2,
            backgroundColor: '#1b1b1b',
            borderColor: '#666666',
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: '#666666',
              },
              '&:hover fieldset': {
                borderColor: '#ffffff',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#00bfa5',
              },
            },
            input: {
              color: '#ffffff',
              padding: '16px',
            },
          }}
          fullWidth
          multiline
          rows={4}
        />
        <CustomButton variant="contained">
          Submit
        </CustomButton>
      </Box>
    </Box>
  );
};

export default Footer;
