// src/components/ContainerCard.jsx
import React from "react";
import { Play, Pause, Trash2, Settings, Cpu, Database, Clock } from "lucide-react";
import { Sparklines, SparklinesLine } from "react-sparklines";
import { motion } from "framer-motion";

export default function ContainerCard({
  id,
  name,
  image,
  status,
  ports,
  uptime,
  cpu = "—",
  memory = "—",
  onStart,
  onStop,
  onRemove,
  onConfigure,
  cpuHistory = [],
  ramHistory = []
}) {
  const isRunning = status === "running" || status === "Running";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.3 }}
      className="relative bg-gradient-to-br from-[#1b1c20]/90 via-[#1c1c24]/80 to-[#16161a]/90 backdrop-blur-xl border border-white/10 p-5 rounded-2xl shadow-[0_0_20px_rgba(0,0,0,0.4)] overflow-hidden group"
    >
      {/* ✨ Light violet hover glow */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-all duration-500 rounded-2xl bg-[radial-gradient(circle_at_top_left,rgba(168,85,247,0.2),transparent_60%)] blur-xl"></div>

      {/* Header */}
      <div className="flex items-start justify-between relative z-10">
        <div>
          <h3 className="text-xl font-semibold text-white tracking-tight">{name}</h3>
          <p className="text-xs text-neutral-400 mt-1">{image}</p>

          <div className="mt-3 flex items-center gap-3">
            {/* Status indicator */}
            <div className="flex items-center gap-2">
              <div
                className={`w-2.5 h-2.5 rounded-full ${
                  isRunning
                    ? "bg-green-400 animate-pulse shadow-[0_0_6px_rgba(74,222,128,0.8)]"
                    : "bg-red-500"
                }`}
              />
              <span
                className={`text-xs font-medium px-3 py-1 rounded-full ${
                  isRunning
                    ? "bg-green-700/20 text-green-300"
                    : "bg-gray-700/20 text-neutral-300"
                }`}
              >
                {isRunning ? "Running" : "Stopped"}
              </span>
            </div>

            <div className="flex items-center gap-1 text-xs text-neutral-400">
              <Clock className="w-3.5 h-3.5 text-purple-300" />
              <span>Uptime:</span>
              <span className="text-white ml-1">{uptime || "—"}</span>
            </div>
          </div>
        </div>

        {/* Metrics */}
        <div className="flex flex-col items-end gap-2 text-right">
          <div>
            <span className="text-neutral-400 text-xs">CPU</span>
            <p className="text-white font-semibold text-sm">{cpu}</p>
          </div>
          <div>
            <span className="text-neutral-400 text-xs">RAM</span>
            <p className="text-white font-semibold text-sm">{memory}</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mt-5 grid grid-cols-3 gap-3 items-center relative z-10">
        <div className="col-span-2">
          <div className="flex items-center gap-3 text-sm text-neutral-400">
            <Cpu className="w-4 h-4 text-purple-300" />
            <div>
              Ports:
              <span className="text-white ml-1">{ports || "—"}</span>
            </div>
            <Database className="w-4 h-4 ml-4 text-purple-300" />
          </div>

          {/* Sparklines */}
          <div className="mt-3 flex gap-4">
            <div className="w-28">
              <Sparklines data={cpuHistory.length ? cpuHistory : [0, 0, 0, 0, 0]}>
                <SparklinesLine
                  style={{
                    strokeWidth: 3,
                    stroke: "rgba(168,85,247,0.9)",
                    fill: "rgba(168,85,247,0.1)",
                  }}
                />
              </Sparklines>
              <p className="text-[10px] text-center text-neutral-500 mt-1">CPU</p>
            </div>
            <div className="w-28">
              <Sparklines data={ramHistory.length ? ramHistory : [0, 0, 0, 0, 0]}>
                <SparklinesLine
                  style={{
                    strokeWidth: 3,
                    stroke: "rgba(147,51,234,0.9)",
                    fill: "rgba(147,51,234,0.1)",
                  }}
                />
              </Sparklines>
              <p className="text-[10px] text-center text-neutral-500 mt-1">RAM</p>
            </div>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex flex-col items-end gap-3">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() =>
              isRunning ? onStop && onStop(id) : onStart && onStart(id)
            }
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isRunning
                ? "bg-yellow-700/20 hover:bg-yellow-700/30 text-yellow-300"
                : "bg-green-700/20 hover:bg-green-700/30 text-green-300"
            }`}
          >
            {isRunning ? (
              <>
                <Pause className="w-4 h-4" /> Stop
              </>
            ) : (
              <>
                <Play className="w-4 h-4" /> Start
              </>
            )}
          </motion.button>

          <div className="flex gap-2">
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => onConfigure && onConfigure(id)}
              className="flex items-center gap-2 bg-purple-700/20 hover:bg-purple-700/30 text-purple-300 px-3 py-2 rounded-md text-sm transition-colors"
            >
              <Settings className="w-4 h-4" /> Configure
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => onRemove && onRemove(id)}
              className="flex items-center gap-2 bg-red-700/20 hover:bg-red-700/30 text-red-300 px-3 py-2 rounded-md text-sm transition-colors"
            >
              <Trash2 className="w-4 h-4" /> Delete
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
