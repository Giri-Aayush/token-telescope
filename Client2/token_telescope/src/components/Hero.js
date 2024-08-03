import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { makeStyles } from "@mui/styles";
import AuthPage from "./AuthPage";

const useStyles = makeStyles((theme) => ({
  heroSection: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    backgroundColor: "black",
    color: "white",
    textAlign: "center",
    padding: theme.spacing(2),
  },
  heroTitle: {
    fontFamily: "Playfair Display, serif",
    fontSize: "3rem",
    marginBottom: theme.spacing(2),
  },
  heroDescription: {
    fontFamily: "Roboto, sans-serif",
    fontSize: "1.2rem",
    maxWidth: "600px",
    marginBottom: theme.spacing(3),
  },
  heroButton: {
    fontFamily: "Roboto, sans-serif",
    fontSize: "1rem",
    padding: theme.spacing(1.5, 4),
    backgroundColor: "#1e88e5",
    color: "white",
    borderRadius: "25px",
    textTransform: "none",
    boxShadow: "0 3px 5px 2px rgba(30, 136, 229, .3)",
    transition: "background-color 0.3s, transform 0.8s",
    "&:hover": {
      backgroundColor: "#1565c0",
      transform: "scale(1.05)",
    },
    
  },
  buttonContainer: {
    display: "flex",
    gap: theme.spacing(2),
  },
}));

const HeroSection = () => {
  const classes = useStyles();
  const handleClick = () => {
    <AuthPage />;
  };
  const handlePay = () => {};
  return (
    <Box className={classes.heroSection}>
      <Typography variant="h1" className={classes.heroTitle}>
        Token Telescopy
      </Typography>
      <Typography variant="body1" className={classes.heroDescription}>
        Behold! The future of contract prediction is here, in your hands. Token
        Telescope uses your public key and nonce to sketch out a landscape
        dotted by predicted addresses. Who says time travel isn’t real? Embrace
        the power.
      </Typography>
      <br></br>
      <Box className={classes.buttonContainer}>
        <Button className={classes.heroButton} onClick={handleClick}>
          Login/Sign Up
        </Button>
        <Button className={classes.heroButton} onClick={handlePay}>
          Pay
        </Button>
      </Box>
    </Box>
  );
};

export default HeroSection;
