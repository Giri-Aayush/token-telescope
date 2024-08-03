import React, { useState } from 'react';
import { Container, Typography, TextField, MenuItem, Button, Box, Alert } from '@mui/material';
import Web3 from 'web3';

const web3 = new Web3(Web3.givenProvider || 'http://localhost:8545');

const Wallet = () => {
  const [currency, setCurrency] = useState('ETH');
  const [amount, setAmount] = useState('');
  const [status, setStatus] = useState('');

  const walletAddress = '0xYourWalletAddress'; // Replace with your wallet address

  const handlePayment = async () => {
    if (!amount || amount <= 0) {
      setStatus('Please enter a valid amount.');
      return;
    }

    try {
      if (currency === 'ETH') {
        await sendEth(walletAddress, amount);
      } else if (currency === 'USDT') {
        await sendUsdt(walletAddress, amount);
      }
      setStatus('Payment successful!');
    } catch (error) {
      setStatus(`Payment failed: ${error.message}`);
    }
  };

  const sendEth = async (to, amount) => {
    const accounts = await web3.eth.requestAccounts();
    const from = accounts[0];
    const value = web3.utils.toWei(amount, 'ether');

    await web3.eth.sendTransaction({ from, to, value });
  };

  const sendUsdt = async (to, amount) => {
    const accounts = await web3.eth.requestAccounts();
    const from = accounts[0];
    const usdtAddress = '0xdAC17F958D2ee523a2206206994597C13D831ec7'; // USDT Contract Address
    const value = web3.utils.toWei(amount, 'mwei'); // USDT uses 6 decimals

    const transactionParameters = {
      to: usdtAddress,
      from,
      data: web3.eth.abi.encodeFunctionCall({
        name: 'transfer',
        type: 'function',
        inputs: [
          {
            type: 'address',
            name: 'recipient'
          },
          {
            type: 'uint256',
            name: 'amount'
          }
        ]
      }, [to, value])
    };

    await web3.eth.sendTransaction(transactionParameters);
  };

  return (
    <Container maxWidth="sm">
      <Box mt={5}>
        <Typography variant="h4" gutterBottom>
          Crypto Wallet
        </Typography>
        <Box mb={3}>
          <TextField
            label="Wallet Address"
            value={walletAddress}
            fullWidth
            margin="normal"
            InputProps={{
              readOnly: true,
            }}
          />
        </Box>
        <Box mb={3}>
          <TextField
            select
            label="Select Currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            fullWidth
            margin="normal"
          >
            <MenuItem value="ETH">ETH</MenuItem>
            <MenuItem value="USDT">USDT</MenuItem>
          </TextField>
          <TextField
            label="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            fullWidth
            margin="normal"
            type="number"
          />
          <Button variant="contained" color="primary" onClick={handlePayment} fullWidth>
            Pay
          </Button>
        </Box>
        {status && (
          <Alert severity={status.includes('successful') ? 'success' : 'error'}>
            {status}
          </Alert>
        )}
      </Box>
    </Container>
  );
};

export default Wallet;
