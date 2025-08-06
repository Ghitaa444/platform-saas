import React from 'react';
import { NavLink } from 'react-router-dom';
import { FaBoxes, FaCog, FaSignOutAlt } from 'react-icons/fa';
import { useAuth } from '../hooks/useAuth';
import { motion } from 'framer-motion';

const navItems = [
    { name: 'اللوحة الرئيسية', icon: <FaBoxes />, path: '/dashboard' },
    { name: 'الإعدادات', icon: <FaCog />, path: '/settings' },
];

export default function Sidebar() {
    const { logout } = useAuth();

    return (
        <motion.div
            initial={{ x: -100 }}
            animate={{ x: 0 }}
            transition={{ duration: 0.5 }}
            className="w-64 bg-gray-900 text-white flex flex-col h-screen p-6 shadow-2xl"
        >
            <div className="flex items-center mb-8">
                <h1 className="text-3xl font-extrabold text-blue-400">
                    SaaS App
                </h1>
            </div>
            <nav className="flex-1 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.name}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center p-3 rounded-lg text-lg transition-colors duration-300 ${isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'}`
                        }
                    >
                        {item.icon}
                        <span className="ml-4 font-medium">{item.name}</span>
                    </NavLink>
                ))}
            </nav>
            <div className="mt-8">
                <button
                    onClick={logout}
                    className="flex items-center p-3 w-full rounded-lg text-lg text-red-400 hover:bg-gray-800 transition-colors duration-300"
                >
                    <FaSignOutAlt />
                    <span className="ml-4 font-medium">تسجيل الخروج</span>
                </button>
            </div>
        </motion.div>
    );
}