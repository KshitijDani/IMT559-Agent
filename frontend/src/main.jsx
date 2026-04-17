import React from "react";
import ReactDOM from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles.css";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";
const shouldBypassGoogleAuth = import.meta.env.ALLOW_DEV_AUTH === "true";

const app = (
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

ReactDOM.createRoot(document.getElementById("root")).render(
  shouldBypassGoogleAuth || !googleClientId ? app : (
    <GoogleOAuthProvider clientId={googleClientId}>{app}</GoogleOAuthProvider>
  )
);
