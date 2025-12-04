// src/components/LoadingSpinner.jsx
import React from "react";

export default function LoadingSpinner({ size = "w-12 h-12", color = "from-primary to-accent" }) {
  return (
    <div className="flex justify-center items-center py-10">
      <div className={`relative ${size}`}>
        <div
          className={`absolute inset-0 rounded-full border-4 border-transparent bg-gradient-to-tr ${color} animate-spin`}
          style={{
            mask: "conic-gradient(transparent 10%, black 100%)",
            WebkitMask: "conic-gradient(transparent 10%, black 100%)",
          }}
        />
        <div className="absolute inset-[20%] bg-card/80 rounded-full backdrop-blur-md shadow-inner"></div>
      </div>
    </div>
  );
}
