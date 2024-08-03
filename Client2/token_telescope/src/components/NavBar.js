import React from 'react';
import { AppBar, Toolbar, Box } from '@mui/material';
import image from "./TT.jpg";
const Navbar = () => {
  return (
    <AppBar position="static" sx={{ backgroundColor: 'black' }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box 
          component="img"
          sx={{
            height: 0,
            width: 'auto',
            maxHeight: { xs: 60, md: 80 },
          }}
          alt="Logo"
          src={image}
        />
        {/* You can add more navbar items here */}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;