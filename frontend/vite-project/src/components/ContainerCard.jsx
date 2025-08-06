import React from 'react';

export default function ContainerCard({ name, image, cpu, memory, ports, uptime, status }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-bold text-lg">{name}</h3>
          <p className="text-sm text-gray-500">{image}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs ${
          status === 'running' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {status}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div>
          <p className="text-sm text-gray-500">CPU Usage</p>
          <p className="font-medium">{cpu}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Memory</p>
          <p className="font-medium">{memory}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Ports</p>
          <p className="font-medium">{ports}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Uptime</p>
          <p className="font-medium">{uptime}</p>
        </div>
      </div>
      
      <div className="flex space-x-2 mt-4">
        <button className="px-3 py-1 bg-gray-200 rounded text-sm">
          Stop
        </button>
        <button className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm">
          Configure
        </button>
        <button className="px-3 py-1 bg-red-100 text-red-800 rounded text-sm">
          Remove
        </button>
      </div>
    </div>
  );
}