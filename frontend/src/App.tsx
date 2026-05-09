import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "../src/pages/Landing";
import Home from "../src/pages/Home";
import Agent from "../src/pages/Agent";
import AgentDetails from "./pages/AgentDetails";
import RegisterProduct from "../src/pages/RegisterProduct";
import SearchResults from "../src/pages/SearchResults";
import { ThemeProvider } from "./context/ThemeProvider";

import { useMemo } from "react";
import { ConnectionProvider, WalletProvider } from "@solana/wallet-adapter-react";
import { WalletModalProvider } from "@solana/wallet-adapter-react-ui";
import { clusterApiUrl } from "@solana/web3.js";
import "@solana/wallet-adapter-react-ui/styles.css";


export default function App() {

  const endpoint = useMemo(() => clusterApiUrl("devnet"), []);
  const wallets = useMemo(() => [], []);

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <ThemeProvider>


            <BrowserRouter>
              <Routes>
                {/* Landing Page: Dual interface - "I'm an Agent" or "I'm a Human" */}
                <Route path="/" element={<Landing />} />

                {/* Agent Integration: Get SKILL.md and API endpoints */}
                <Route path="/agent" element={<Agent />} />

                {/* Human Search Interface: Search and discover skills */}
                <Route path="/home" element={<Home />} />

                {/* Human Registration: Register agentic products */}
                <Route path="/register" element={<RegisterProduct />} />

                {/* Search Results: Display query results */}
                <Route path="/search" element={<SearchResults />} />

                <Route path="/agent/:id" element={<AgentDetails />} />

              </Routes>
            </BrowserRouter>
          </ThemeProvider>
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}