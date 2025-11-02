import { Link } from 'react-router-dom';
import '../index.css'

export default function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-left">
                <Link to="/">
                    <span className="nav-element">OrderFlow</span>
                </Link>
            </div>
            <div className="navbar-center">
                <span className="nav-element">Welcome • Saturday, Nov 1</span>
            </div>
            <div className="navbar-right">
                <span className="nav-element">Sales Calls</span>
            </div>     
        </nav>
    )
}