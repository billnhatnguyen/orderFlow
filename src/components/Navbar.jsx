import { Link } from 'react-router-dom';
import '../index.css'

export default function Navbar() {
    const now = new Date();
    const dateStr = now.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
    const scrollToHeader = () => {
        const el = document.querySelector('.header');
        if (el) {
            // Scroll to just after the header so the content below becomes visible.
            const target = el.offsetTop + el.offsetHeight;
            window.scrollTo({ top: target, behavior: 'smooth' });
        } else {
            // fallback: scroll to bottom
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' || e.key === ' ') scrollToHeader();
    };

    return (
        <nav className="navbar">
            <div className="navbar-left">
                <Link to="/">
                    <span className="nav-element">OrderFlow</span>
                </Link>
            </div>
            <div className="navbar-center">
                <span className="nav-element">Welcome • {dateStr}</span>
            </div>
            <div className="navbar-right">
                <span
                    className="nav-element nav-clickable"
                    role="button"
                    tabIndex={0}
                    onClick={scrollToHeader}
                    onKeyDown={handleKeyDown}
                >
                    Sales Calls
                </span>
            </div>
        </nav>
    )
}