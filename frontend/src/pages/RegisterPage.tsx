
import api from "../utils/api";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
const RegisterPage: React.FC = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmation, setConfirmation] = useState("");
    const [error, setError] = useState("");
    
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            const response = await api.post("/threads/users/", { username, email, password, confirmation });
            if (response.status === 201) {
                navigate("/");
            }
        } catch (error: any) {
            if (error.response && error.response.data) {
                setError(error.response.data.error);
            } else {
                setError("Registration failed. Please try again.");
            }
        }
    };
    return (
    <div>
        <div className="pt-28 pb-14 md:px-6 md:py-0 flex flex-1 flex-col items-center justify-center w-full h-full">
            <div className="mobile_content_section md:desktop_content_section flex flex-col max-w-sm h-[400px] md:h-[500px] px-10 py-5 rounded-xl">
                {error && <p className="text-red-500 mb-2">{error}</p>}
                <form onSubmit={handleSubmit} noValidate className="flex flex-col justify-center items-center w-full min-w-[100px] h-full">
                    <div id="page-name" className="page_title hidden pageName md:flex justify-center items-center w-32 mb-5 "></div>
                        <input className="form-control auth-input" autoFocus  type="text"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            required />
                        <input className="form-control auth-input" type="email" name="email" placeholder="Email Address"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            required />
                        <input className="form-control auth-input" type="password" name="password" placeholder="Password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required />
                        <input className="form-control auth-input" type="password" name="confirmation" placeholder="Confirm Password"
                            value={confirmation}
                            onChange={e => setConfirmation(e.target.value)}
                            required />
                    <button className=" auth-btn font-medium mt-12" type="submit">Register</button>
                </form>
                
                <div className="text-nowrap text-gray-500 mt-3">
                    Already have an account? <a href="/login" className="font-bold" >Log In here.</a>
                </div>
            </div>
        </div>
    </div>
  );
}
export default RegisterPage