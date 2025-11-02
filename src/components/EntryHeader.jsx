import { useLocation } from 'react-router-dom';

export default function EntryHeader() {
    const location = useLocation();

    // read title/image from Link state if present; otherwise fall back to defaults
    const state = location.state || {};
    const entryTitle = state.title || 'Entry Details';
    const entryImage = state.image || null;

    const now = new Date();
    const dateStr = now.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });


    return (
        
        <header>
            <video
                autoPlay
                loop
                muted
                playsInline
                className="background-video"
            >
                <source src="/images/pizza.mp4" type="video/mp4" />
                Your browser does not support the video tag.
            </video>

            <div className="video-overlay"></div>

            <h1>{entryTitle}</h1>
            <p>{dateStr}</p>
        </header>
    );
}