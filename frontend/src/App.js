import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { Toaster } from "@/components/ui/sonner";
import ProtectedRoute from "@/components/ProtectedRoute";
import Layout from "@/components/layout/Layout";
import Login from "@/pages/Login";
import Signup from "@/pages/Signup";
import Dashboard from "@/pages/Dashboard";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="create" element={<div className="text-white">Create Video - Coming Soon</div>} />
            <Route path="videos" element={<div className="text-white">Video Library - Coming Soon</div>} />
            <Route path="analytics" element={<div className="text-white">Analytics - Coming Soon</div>} />
            <Route path="accounts" element={<div className="text-white">Accounts - Coming Soon</div>} />
            <Route path="settings" element={<div className="text-white">Settings - Coming Soon</div>} />
          </Route>
        </Routes>
        <Toaster />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
