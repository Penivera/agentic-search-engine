import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "../src/pages/Landing";
import Home from "../src/pages/Home";
import Agent from "../src/pages/Agent";
import RegisterProduct from "../src/pages/RegisterProduct";
import SearchResults from "../src/pages/SearchResults";
import { ThemeProvider } from "./context/ThemeProvider";


export default function App() {
  return (
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
        
      </Routes>
    </BrowserRouter>
    </ThemeProvider>
  );
}