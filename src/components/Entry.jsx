import { Link } from "react-router-dom";

// Entry receives an optional `state` prop (the full entry object created in SalesQueue)
export default function Entry({ id = "??", title = "", image = "src/images/pumpkin.png", state = null }) {
    // forward provided state into the Link so EntryDetails can read full order metadata
    const linkState = state || { id, title, image };

    return (
        <Link
            to={`/entry/${id}`}
            state={linkState}
            onClick={() => window.scrollTo({ top: 0, left: 0, behavior: 'auto' })}
        >
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