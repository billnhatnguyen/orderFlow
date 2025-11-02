
import { useParams, Link, useLocation } from 'react-router-dom';
import Navbar from '../components/Navbar';
import EntryHeader from '../components/EntryHeader';
import CustomerInfo from '../components/CustomerInfo';
import './EntryDetails.css';
import EntryScroll from '../components/EntryScroll';

export default function EntryDetails() {
    const { entryId } = useParams();
    const location = useLocation();

    // read title/image from Link state if present; otherwise fall back to a basic default
    const state = location.state || {};
    const entryTitle = state.title || `Entry Details #${entryId}`;
    const entryImage = state.image || null;

    return (
        <>
            <Navbar />
            <EntryHeader />
            <CustomerInfo />
            <EntryScroll />
        </>
    );
}