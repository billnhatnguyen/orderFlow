import { useParams, useLocation } from "react-router-dom";
import { getDatabase, ref, get } from "firebase/database";
import app from "../Firebase.jsx";
import React, { useState, useEffect } from "react";

export default function CustomerInfo() {
  const location = useLocation();
  const state = location.state || {};
  const { entryId } = useParams();

  // Accept either state.orderId (from SalesQueue entry) or state.orderKey,
  // or fall back to parsing the route param (composite id like orderId-0)
  const derivedOrderKey = state.orderId || state.orderKey || (entryId && entryId.includes('-') ? entryId.split('-')[0] : (entryId || null));
  const orderKey = derivedOrderKey;
  const [order, setOrder] = useState(null);

  useEffect(() => {
    if (!orderKey) return;

    const fetchOrder = async () => {
      try {
        const db = getDatabase(app);
        const snapshot = await get(ref(db, `orders/${orderKey}`));
        if (snapshot.exists()) setOrder(snapshot.val());
        else setOrder(null);
      } catch (err) {
        console.error('Error fetching order in CustomerInfo:', err);
        setOrder(null);
      }
    };

    fetchOrder();
  }, [orderKey]);

  if (!order) return <p>Loading customer info...</p>;

  return (
    <main>
      <h1>Customer Info</h1>
      <p><strong>Name:</strong> {order.name}</p>
      <p><strong>Phone:</strong> {order.phoneNumber}</p>
      <p><strong>Pickup:</strong> {order.pickUpLocation}</p>
      <p><strong>Total:</strong> ${order.totalPrice}</p>
      <p><strong>Items:</strong></p>
      <ul>
        {order.orderDetails.map((item, i) => (
          <li key={i}>
            {item.quantity} x {item.itemName} (${item.price})
          </li>
        ))}
      </ul>
    </main>
  );
}
