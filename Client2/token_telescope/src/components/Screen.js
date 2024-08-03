import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LoginPage from "./AuthPage";
import PayPage from "./PayPage";
import PredictPage from "./PredictPage";
import { AuthProvider } from "./AuthContext";
import Wallet from "./Wallet";
import HeroSection from "./Hero";
export default function Screen() {
  return (
    <div>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" exact element={<LoginPage />} />
            <Route path="/predict" exact element={<PredictPage />} />
            <Route path="/pay" exact element={<PayPage />} />
            <Route path="/wallet" exact element={<Wallet />} /> 
            {/* <Route path="/" exact element={<HeroSection />} /> */}
          </Routes>
        </Router>
      </AuthProvider>
    </div>
  );
}
