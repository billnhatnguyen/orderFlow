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
                    id={index + 1}            // entry number for display
                    title={entry.title}
                    image={entry.image}
                    state={{ orderKey: entry.orderId }} // pass the Firebase key
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
  if (lower.includes("pizza")) return "src/images/food.png";
  if (lower.includes("salad")) return "src/images/apple.png";
  if (lower.includes("soup")) return "src/images/pumpkin.png";
  return "src/images/default.png";
}
