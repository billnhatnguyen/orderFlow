import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Header from "./components/Header.jsx";
import SalesQueue from "./components/SalesQueue.jsx";
import '../index.css';

export default function Home() {
  return (
    <>
      <Navbar/>
      <Header/>
      <SalesQueue/>
    </>  
  )
}