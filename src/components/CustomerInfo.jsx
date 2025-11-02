import React, { useState, useEffect } from 'react';
import app from "../Firebase.jsx";
import { getDatabase, ref, get } from "firebase/database";

export default function CustomerInfo() {
  const [userArray, setUserArray] = useState([]);

  const fetchData = async () => {
    try {
      const db = getDatabase(app);
      const dbRef = ref(db, "nature/fruits");
      const snapshot = await get(dbRef);
      if (snapshot.exists()) {
        // Assuming each child has fields like { name: "...", ... }
        setUserArray(Object.values(snapshot.val()));
      } else {
        console.warn("No data found at this path");
      }
    } catch (error) {
      console.error("Error fetching data from Firebase:", error);
    }
  };

  // Run once when the component mounts
  useEffect(() => {
    fetchData();
  }, []);

  return (
    <main>
      <h1>Customer Info</h1>
      <ul className="customer-info">
        {userArray.length === 0 ? (
          <li>Loading or no data available</li>
        ) : (
          userArray.map((item, index) => (
            <li key={index}>
              Name: {item.name}
            </li>
          ))
        )}
      </ul>
    </main>
  );
}