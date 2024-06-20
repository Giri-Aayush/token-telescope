"use client";
import React from "react";
import { Box, Typography } from "@mui/material";
import { styled } from "@mui/system";

const Container = styled(Box)(({ theme }) => ({
  height: '7rem',
  width: 'fit-content',
  backgroundColor: 'black',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  overflow: 'hidden',
  borderRadius: theme.shape.borderRadius,
  marginBottom: theme.spacing(5),
  [theme.breakpoints.up('sm')]: {
    marginBottom: theme.spacing(10),
  },
}));

const Heading = styled(Typography)(({ theme }) => ({
  fontSize: '5rem',
  fontWeight: 'bold',
  textAlign: 'center',
  color: 'white',
  position: 'relative',
  zIndex: 20,
  [theme.breakpoints.up('sm')]: {
    fontSize: '6rem',
  },
  [theme.breakpoints.up('md')]: {
    fontSize: '7rem',
  },
  [theme.breakpoints.up('lg')]: {
    fontSize: '6rem',
  },
}));

const GradientContainer = styled(Box)(({ theme }) => ({
  width: '20rem',
  height: '5rem',
  position: 'relative',
  marginRight: theme.spacing(4),
  [theme.breakpoints.up('sm')]: {
    width: '25rem',
  },
}));

const Gradient1 = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: '20%',
  right: '20%',
  height: '2px',
  width: '75%',
  background: 'linear-gradient(to right, transparent, #5a67d8, transparent)',
  filter: 'blur(2px)',
}));

const Gradient2 = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: '20%',
  right: '20%',
  height: '1px',
  width: '75%',
  background: 'linear-gradient(to right, transparent, #5a67d8, transparent)',
}));

const Gradient3 = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: '60%',
  right: '60%',
  height: '5px',
  width: '25%',
  background: 'linear-gradient(to right, transparent, #38b2ac, transparent)',
  filter: 'blur(5px)',
}));

const Gradient4 = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: '60%',
  right: '60%',
  height: '1px',
  width: '25%',
  background: 'linear-gradient(to right, transparent, #38b2ac, transparent)',
}));

export default function SparklesLogo() {
  return (
    <Container>
      <Heading>
        DHF
      </Heading>
      <GradientContainer>
        {/* Gradients */}
        <Gradient1 />
        <Gradient2 />
        <Gradient3 />
        <Gradient4 />

        {/* Core component */}
        {/* <SparklesCore
          background="transparent"
          minSize={0.4}
          maxSize={1}
          particleDensity={1200}
          className="w-full h-full"
          particleColor="#FFFFFF"
        /> */}

        {/* Radial Gradient to prevent sharp edges */}
        {/* <div className="absolute inset-0 w-full h-full bg-transparent [mask-image:radial-gradient(350px_200px_at_top,transparent_20%,white)]"></div> */}
      </GradientContainer>
    </Container>
  );
}
