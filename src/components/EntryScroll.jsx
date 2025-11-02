import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getDatabase, ref, get } from "firebase/database";
import app from "../Firebase.jsx";

// Optional helper to match image based on item name
function getImageForItem(name) {
  const lower = name.toLowerCase();
  if (lower.includes("pepperoni")) return "/images/pepperoni.png";
  if (lower.includes("bbq")) return "/images/bbq.png";
  if (lower.includes("chicken")) return "/images/chicken.png";
  if (lower.includes("margherita")) return "/images/margherita.png";
  if (lower.includes("veggie")) return "/images/veggie.png";
  if (lower.includes("hawaiian")) return "/images/hawaiian.png";
  return "public/images/default.png";
}

export default function EntryScroll() {
    const { entryId } = useParams();
    const [entries, setEntries] = useState([]);

    useEffect(() => {
      const fetchEntries = async () => {
        try {
          const db = getDatabase(app);
          const ordersRef = ref(db, "orders");
          const snapshot = await get(ordersRef);

          if (!snapshot.exists()) {
            setEntries([]);
            return;
          }

          const orders = snapshot.val();
          const newEntries = [];

          Object.entries(orders).forEach(([orderId, order]) => {
            if (Array.isArray(order.orderDetails)) {
              order.orderDetails.forEach((item, index) => {
                newEntries.push({
                  id: `${orderId}-${index}`,
                  title: item.itemName,
                  image: getImageForItem(item.itemName),
                  orderId,
                });
              });
            }
          });

          setEntries(newEntries);
        } catch (err) {
          console.error("Error loading entries for EntryScroll:", err);
          setEntries([]);
        }
      };

      fetchEntries();
    }, []);

    // if entries not loaded yet, don't render navigation
    if (!entries || entries.length === 0) return null;

    // Find the current entry's index using the composite id
    const currentIndex = entries.findIndex(e => e.id === entryId);
    const prevEntry = currentIndex > 0 ? entries[currentIndex - 1] : null;
    const nextEntry = currentIndex >= 0 && currentIndex < entries.length - 1 ? entries[currentIndex + 1] : null;

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