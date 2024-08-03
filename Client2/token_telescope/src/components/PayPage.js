import React from 'react';
import { Box, Typography, Button, Grid } from '@mui/material';

const MinimalistButton = ({ children, onClick }) => (
  <Button
    onClick={onClick}
    sx={{
      bgcolor: 'black',
      color: 'white',
      border: '2px solid white',
      borderRadius: 0,
      padding: '10px 20px',
      fontWeight: 'bold',
      transition: 'all 0.3s',
      '&:hover': {
        bgcolor: 'white',
        color: 'black',
      },
    }}
  >
    {children}
  </Button>
);

const PlanOption = ({ title, price, feature, link }) => (
  <Box
    sx={{
      border: '2px solid white',
      p: 4,
      textAlign: 'center',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    }}
  >
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2 }}>
        {title}
      </Typography>
      <Typography variant="h6" sx={{ mb: 2 }}>
        {price} USDT
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        {feature}
      </Typography>
    </Box>
    <MinimalistButton onClick={() => window.location.href = link}>
      {title}
    </MinimalistButton>
  </Box>
);

const PaymentPage = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'black',
        color: 'white',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
      }}
    >
      <Typography variant="h2" sx={{ fontWeight: 'bold', mb: 6, textAlign: 'center' }}>
        Choose Your Plan
      </Typography>
      <Grid container spacing={4} maxWidth="lg">
        <Grid item xs={12} md={4}>
          <PlanOption
            title="Basic"
            price={10}
            feature="50 Contract Addresses"
            link="https://commerce.coinbase.com/checkout/c8d70817-6284-4e5a-890c-1237e0c2dd40"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <PlanOption
            title="Standard"
            price={20}
            feature="150 Contract Addresses"
            link="https://commerce.coinbase.com/checkout/019e71b8-752e-457d-89cf-5d782624aab2"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <PlanOption
            title="Premium"
            price={100}
            feature="Lifetime Usage"
            link="https://commerce.coinbase.com/checkout/a761619b-6995-4480-8f13-4527f3c75792"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default PaymentPage;