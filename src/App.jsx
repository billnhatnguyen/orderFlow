import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Header from "./components/Header.jsx";
import SalesQueue from "./components/SalesQueue.jsx";
import EntryDetails from "./pages/EntryDetails.jsx";
import './index.css';

function Home() {
  return (
    <>
      <Navbar />
      <Header />
      <SalesQueue />
    </>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/entry/:entryId" element={<EntryDetails />} />
      </Routes>
    </Router>
  )
}