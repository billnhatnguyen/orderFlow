import React, { useState, useEffect } from "react";
import { getDatabase, ref, onValue } from "firebase/database";
import app from "../Firebase.jsx";
import Entry from "./Entry";

export default function SalesQueue() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    const db = getDatabase(app);
    const ordersRef = ref(db, "orders");

    const unsubscribe = onValue(ordersRef, (snapshot) => {
      if (snapshot.exists()) {
        const orders = snapshot.val();
        const newEntries = [];

        Object.entries(orders).forEach(([orderId, order]) => {
          if (Array.isArray(order.orderDetails)) {
            order.orderDetails.forEach((item, index) => {
              newEntries.push({
                id: `${orderId}-${index}`, // unique identifier for Link
                title: item.itemName,
                image: getImageForItem(item.itemName), // optional helper
                orderId,
                name: order.name,
                phoneNumber: order.phoneNumber,
                totalPrice: order.totalPrice,
                quantity: item.quantity,
                price: item.price,
                pickUpLocation: order.pickUpLocation,
                timestamp: order.timestamp
              });
            });
          }
        });

        setEntries(newEntries);
      } else {
        setEntries([]);
      }
    });

    return () => unsubscribe();
  }, []);

  return (
    <main>
      <div className="info-text">
        <h2>Lettuce Begin!</h2>
        <p>Check out your sales calls queue below!</p>
      </div>

      <div className="entries">
            {entries.length === 0 ? (
                <p>Loading or no data available...</p>
            ) : (
        entries.map((entry, index) => (
        <Entry
          key={entry.id}
          id={entry.id}            // use composite id for URL
          title={entry.title}
          image={entry.image}
          state={entry}           // pass full entry metadata
          displayNumber={index + 1} // friendly sequential number for UI
        />
        ))
            )}
        </div>
    </main>
  );
}

// Optional helper to match image based on item name
function getImageForItem(name) {
  const lower = name.toLowerCase();
  if (lower.includes("pepperoni")) return "public/images/pepperoni.png";
  if (lower.includes("bbq")) return "public/images/bbq.png";
  if (lower.includes("chicken")) return "public/images/chicken.png";
  if (lower.includes("margherita")) return "public/images/margherita.png";
  if (lower.includes("veggie")) return "public/images/veggie.png";
  if (lower.includes("hawaiian")) return "public/images/hawaiian.png";
  return "public/images/default.png";
}
