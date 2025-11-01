export default function SalesQueue() {
    return (
        <main>
            <div className="info-text">
                <h2>Lettuce Begin!</h2>
                <p>Check out your sales calls queue below!</p>
            </div>

            <div className="entries">
                <div className="entry">
                    <div className="entry-number">
                        <span>Entry</span>
                        <span>#01</span>
                    </div>

                    <img src="src/images/food.png" className="food-item-img" alt="Plate of tomato basil pasta"/>

                    <span>Tomato Basil Pasta</span>
                    <img src="src/images/Button.png" className="arrow-btn" alt="arrow pointing to the downwards right direction"/>
                </div>

                <div className="entry">
                    <div className="entry-number">
                        <span>Entry</span>
                        <span>#02</span>
                    </div>

                    <img src="src/images/apple.png" className="food-item-img" alt="An apple"/>

                    <span>Apple Citrus Salad</span>
                    <img src="src/images/Button.png" className="arrow-btn" alt="arrow pointing to the downwards right direction"/>
                </div>

                <div className="entry">
                    <div className="entry-number">
                        <span>Entry</span>
                        <span>#03</span>
                    </div>

                    <img src="src/images/pumpkin.png" className="food-item-img" alt="Pumpkin"/>

                    <span>Pumpkin Soup</span>
                    <img src="src/images/Button.png" className="arrow-btn" alt="arrow pointing to the downwards right direction"/>
                </div>
            </div>

        </main>
    )
}