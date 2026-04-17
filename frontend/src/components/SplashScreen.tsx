import React from 'react';
import { motion } from 'framer-motion';
import logo from '../assets/logo.png';

const SplashScreen: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8, ease: "easeInOut" }}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black"
    >
      <div className="relative w-64 h-64 md:w-96 md:h-96">
        {/* Main Logo Animation */}
        <motion.img
          src={logo}
          alt="Logo"
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ 
            scale: [0.5, 1.2, 50],
            opacity: [0, 1, 1, 0],
          }}
          transition={{ 
            duration: 3, 
            times: [0, 0.2, 0.9, 1],
            ease: "circIn" 
          }}
          className="w-full h-full object-contain"
        />

        {/* Ambient Glow Effect */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: [0, 0.4, 0], scale: [0.8, 1.2, 2] }}
          transition={{ duration: 2, times: [0, 0.5, 1] }}
          className="absolute inset-0 bg-indigo-500/10 blur-[100px] rounded-full"
        />
      </div>
    </motion.div>
  );
};

export default SplashScreen;
