import { useParams, Link } from "react-router-dom";
import Entry from "./Entry";

// Import images
import foodImg from "../images/food.png";
import appleImg from "../images/apple.png";
import pumpkinImg from "../images/pumpkin.png";

// Array of all entries for navigation
const entries = [
    {
        id: "01",
        title: "Tomato Basil Pasta",
        image: foodImg
    },
    {
        id: "02",
        title: "Apple Citrus Salad",
        image: appleImg
    },
    {
        id: "03",
        title: "Pumpkin Soup",
        image: pumpkinImg
    }
];

export default function EntryScroll() {
    const { entryId } = useParams();
    
    // Find the current entry's index
    const currentIndex = entries.findIndex(entry => entry.id === entryId);
    
    // Get previous and next entries
    const prevEntry = currentIndex > 0 ? entries[currentIndex - 1] : null;
    const nextEntry = currentIndex < entries.length - 1 ? entries[currentIndex + 1] : null;

    return (
        <div className="entry-scroll">
            <div className="entry-navigation">
                {prevEntry && (
                    <Link 
                        to={`/entry/${prevEntry.id}`} 
                        state={prevEntry}
                        className="nav-button prev"
                        onClick={() => window.scrollTo({ top: 0, left: 0, behavior: 'auto' })}
                    >
                        <div className="nav-content">
                            <img src={prevEntry.image} alt={prevEntry.title} className="nav-image" />
                            <div className="nav-text">
                                <span>← Previous</span>
                                <small>{prevEntry.title}</small>
                            </div>
                        </div>
                    </Link>
                )}
                
                {nextEntry && (
                    <Link 
                        to={`/entry/${nextEntry.id}`} 
                        state={nextEntry}
                        className="nav-button next"
                        onClick={() => window.scrollTo({ top: 0, left: 0, behavior: 'auto' })}
                    >
                        <div className="nav-content">
                            <div className="nav-text">
                                <span>Next →</span>
                                <small>{nextEntry.title}</small>
                            </div>
                            <img src={nextEntry.image} alt={nextEntry.title} className="nav-image" />
                        </div>
                    </Link>
                )}
            </div>
        </div>
    );
}