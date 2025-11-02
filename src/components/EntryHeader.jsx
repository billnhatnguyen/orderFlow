import { useLocation } from 'react-router-dom';

export default function EntryHeader() {
    const location = useLocation();

    // read title/image from Link state if present; otherwise fall back to defaults
    const state = location.state || {};
    const entryTitle = state.title || 'Entry Details';
    const entryImage = state.image || null;

    // inline style to set header background to the entry image when available


    return (
        <header>
            <h1>{entryTitle}</h1>
            <p>Saturday, Nov 1</p>
        </header>
    );
}