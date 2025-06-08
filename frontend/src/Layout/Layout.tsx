import { Outlet } from "react-router";
import DesktopNavbar from "./DesktopNavbar";
import MobileNavbarTop from "./MobileNavbarTop";

const Layout: React.FC = () => {
    return (
        <div className="relative min-h-screen min-w-screen">
            <div className="absolute -z-10 inset-0 bg-network"></div>
            <header className="relative z-10">
                <DesktopNavbar className="hidden md:block fixed w-16 h-full left-0 top-0" /> 
                <MobileNavbarTop className="md:hidden fixed w-full top-0 h-24" />
            </header>
            <Outlet />
        </div>
    )
}

export default Layout;