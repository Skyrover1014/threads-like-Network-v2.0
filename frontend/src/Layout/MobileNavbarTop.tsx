import { Link } from "react-router-dom";

const MobileNavbarTop: React.FC<{ className?: string }> = ({ className }) => {
    return (
        <nav className={`${className} bg-white shadow-lg`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center py-6">
                    <div className="flex items-center">
                        <Link to="/" className="text-2xl font-bold text-blue-500">Threads</Link>
                    </div>
                </div> 
            </div>
        </nav>
    )
}

export default MobileNavbarTop;