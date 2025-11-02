import { Link } from "react-router-dom";

export default function Entry({ id = "??", title = "", image = "src/images/pumpkin.png" }) {
    // pass the entry data via Link 'state' so the details page can read it
    return (
        <Link to={`/entry/${id}`} state={{ id, title, image }}>
            <div className="entry">
                <div className="entry-number">
                    <span>Entry</span>
                    <span>#{id}</span>
                </div>

                <img src={image} className="food-item-img" alt={title}/>

                <span>{title}</span>
                <div className="arrow-btn">
                    <img src="src/images/Button.png"/>
                </div>
            </div>
        </Link>
    )
}