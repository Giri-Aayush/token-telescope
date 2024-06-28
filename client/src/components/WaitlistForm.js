import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
} from "@mui/material";
import { styled } from "@mui/system";
import axios from "axios";

const GradientText = styled(Typography)({
  background: "linear-gradient(to bottom, #cccccc, #666666)",
  WebkitBackgroundClip: "text",
  WebkitTextFillColor: "transparent",
});

const CustomButton = styled(Button)({
  height: "48px",
  background: "linear-gradient(110deg, #000103 45%, #1e2631 55%, #000103)",
  backgroundSize: "200% 100%",
  color: "#b3b3b3",
  border: "1px solid #666666",
  marginTop: "24px",
  "&:hover": {
    background: "linear-gradient(110deg, #1e2631 45%, #000103 55%, #1e2631)",
  },
});

const BackgroundBeams = styled("div")({
  position: "absolute",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  background: "url(/path/to/background-beams.png)", // Replace with your background image path
  zIndex: 1,
  opacity: 0.2,
});

function WaitlistForm() {
  const [chain, setChain] = useState("Ethereum Mainnet");
  const [customNonce, setCustomNonce] = useState(false);
  const [nonce, setNonce] = useState("");
  const [walletAddress, setWalletAddress] = useState("");
  const [predictedAddress, setPredictedAddress] = useState(null);
  const [balance, setBalance] = useState(null);

  const handleChainChange = (event) => {
    setChain(event.target.value);
  };

  const handleCustomNonceChange = (event) => {
    setCustomNonce(event.target.checked);
  };

  const handleNonceChange = (event) => {
    setNonce(event.target.value);
  };

  const handleWalletAddressChange = (event) => {
    setWalletAddress(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      window.location.href = "https://commerce.coinbase.com/checkout/019e71b8-752e-457d-89cf-5d782624aab2";
      const response = await axios.post("http://127.0.0.1:5000/predict", {
        contractAddress: walletAddress,
        nonce: customNonce ? parseInt(nonce, 10) : 0,
      });
  
      console.log(response);
      setPredictedAddress(response.data.predictedAddress);
      setBalance(response.data.balance);
    } catch (error) {
      console.error("Error predicting contract address:", error);
    }
  };

  return (
    <Box
      id="waitlist-form"
      sx={{
        marginX: { lg: "auto", sm: 10, xs: 7 },
        marginY: 10,
        maxWidth: "910px",
        paddingY: { sm: 16, xs: 8 },
        width: { lg: "full", sm: "auto", xs: "auto" },
        borderRadius: "16px",
        border: "1px solid #666666",
        backgroundColor: "black",
        position: "relative",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
      }}
    >
      <Box
        sx={{
          minWidth: "960px",
          paddingLeft: 8,
          paddingRight: 8,
          display: "flex",
          flexDirection: "column",
          zIndex: 2,
        }}
      >
        <GradientText
          variant="h1"
          sx={{ fontSize: { md: "4rem", xs: "2.5rem" }, fontWeight: "bold" }}
        >
          Contract Address Predictor{" "}
        </GradientText>
        <br></br>
        <TextField
          type="text"
          placeholder="Ex: 0xD5a63CCE627372481b30AE24c31a3Fb94913D5Be"
          label="Wallet Address"
          variant="outlined"
          value={walletAddress}
          onChange={handleWalletAddressChange}
          sx={{
            marginTop: 3,
            backgroundColor: "#1b1b1b",
            borderColor: "#666666",
            "& .MuiOutlinedInput-root": {
              "& fieldset": {
                borderColor: "#666666",
              },
              "&:hover fieldset": {
                borderColor: "#ffffff",
              },
              "&.Mui-focused fieldset": {
                borderColor: "#00bfa5",
              },
            },
            input: {
              color: "#ffffff",
              padding: "16px",
            },
          }}
          fullWidth
        />
        <FormControl fullWidth sx={{ marginTop: 3 }}>
          <InputLabel id="select-chain-label">Select Chain</InputLabel>
          <Select
            labelId="select-chain-label"
            id="select-chain"
            value={chain}
            label="Select Chain"
            onChange={handleChainChange}
            sx={{
              backgroundColor: "#1b1b1b",
              color: "#ffffff",
              "& .MuiOutlinedInput-notchedOutline": {
                borderColor: "#666666",
              },
              "&:hover .MuiOutlinedInput-notchedOutline": {
                borderColor: "#ffffff",
              },
              "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                borderColor: "#00bfa5",
              },
            }}
          >
            <MenuItem value={"Ethereum Mainnet"}>Ethereum Mainnet</MenuItem>
            <MenuItem value={"Binance Smart Chain"}>
              Binance Smart Chain
            </MenuItem>
            <MenuItem value={"Polygon"}>Polygon</MenuItem>
          </Select>
        </FormControl>

        <FormControlLabel
          control={
            <Switch
              checked={customNonce}
              onChange={handleCustomNonceChange}
              color="primary"
            />
          }
          label="Set Custom Nonce"
          sx={{ marginTop: 3, color: "#ffffff" }}
        />

        {customNonce && (
          <TextField
            type="text"
            placeholder="Ex: 135"
            label="Nonce (Default Value is fetched from Chain)"
            variant="outlined"
            value={nonce}
            onChange={handleNonceChange}
            sx={{
              marginTop: 3,
              backgroundColor: "#1b1b1b",
              borderColor: "#666666",
              "& .MuiOutlinedInput-root": {
                "& fieldset": {
                  borderColor: "#666666",
                },
                "&:hover fieldset": {
                  borderColor: "#ffffff",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#00bfa5",
                },
              },
              input: {
                color: "#ffffff",
                padding: "16px",
              },
            }}
            fullWidth
          />
        )}

        <CustomButton variant="contained" onClick={handleSubmit}>
          Submit
        </CustomButton>

        {predictedAddress && (
          <Typography variant="h6" sx={{ marginTop: 3, color: "#ffffff" }}>
            Predicted Address: {predictedAddress}
          </Typography>
        )}

        {balance !== null && (
          <Typography variant="h6" sx={{ marginTop: 1, color: "#ffffff" }}>
            Balance: {balance} ETH
          </Typography>
        )}
      </Box>
      <BackgroundBeams />
    </Box>
  );
}

export default WaitlistForm;
