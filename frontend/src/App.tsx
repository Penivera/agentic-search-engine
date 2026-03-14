import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "../src/pages/Home";
import SearchResults from "../src/pages/SearchResults";
import Dashboard from "../src/pages/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing Page: The clean, minimalist entry point */}
        <Route path="/" element={<Home />} />
        
        {/* Results Page: Where queries live (e.g., /search?q=query) */}
        <Route path="/search" element={<SearchResults />} />
        
        {/* Search Console: The developer dashboard */}
        <Route path="/console" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}