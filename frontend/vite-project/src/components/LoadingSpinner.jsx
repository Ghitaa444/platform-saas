import React from 'react';

export default function LoadingSpinner({ size = 'w-10 h-10', color = 'text-blue-600' }) {
    return (
        <div className={`flex justify-center items-center`}>
            <div
                className={`animate-spin rounded-full border-4 border-t-4 border-gray-200 ${color} ${size}`}
            />
        </div>
    );
}