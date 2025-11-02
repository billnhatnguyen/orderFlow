import Entry from "./Entry"

export default function SalesQueue() {
    return (
        <main>
            <div className="info-text">
                <h2>Lettuce Begin!</h2>
                <p>Check out your sales calls queue below!</p>
            </div>

            <div className="entries">
                <Entry 
                    id="01" 
                    title="Tomato Basil Pasta" 
                    image="src/images/food.png"
                />
                <Entry 
                    id="02" 
                    title="Apple Citrus Salad" 
                    image="src/images/apple.png"
                />
                <Entry 
                    id="03" 
                    title="Pumpkin Soup" 
                    image="src/images/pumpkin.png"
                />  
            </div>

        </main>
    )
}