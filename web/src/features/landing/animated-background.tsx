import { motion, useReducedMotion } from "framer-motion"

/**
 * Purely decorative — aria-hidden, and collapses to a static gradient
 * for users with prefers-reduced-motion set (checked via Framer
 * Motion's useReducedMotion, not a hardcoded assumption).
 */
export function AnimatedBackground() {
  const reduceMotion = useReducedMotion()

  const orbs = [
    { className: "bg-cyan-500/25 dark:bg-cyan-400/15", size: 480, x: "10%", y: "-10%", duration: 22 },
    { className: "bg-violet-500/20 dark:bg-violet-400/10", size: 420, x: "70%", y: "10%", duration: 26 },
    { className: "bg-cyan-400/15 dark:bg-cyan-300/10", size: 360, x: "40%", y: "60%", duration: 30 },
  ]

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 -z-10 overflow-hidden"
    >
      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,transparent,var(--background))]" />

      {orbs.map((orb, i) => (
        <motion.div
          key={i}
          className={`absolute rounded-full blur-3xl ${orb.className}`}
          style={{
            width: orb.size,
            height: orb.size,
            left: orb.x,
            top: orb.y,
          }}
          animate={
            reduceMotion
              ? undefined
              : {
                  x: [0, 40, -20, 0],
                  y: [0, -30, 20, 0],
                }
          }
          transition={{
            duration: orb.duration,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      <svg
        className="absolute inset-0 h-full w-full opacity-[0.03] dark:opacity-[0.05]"
        aria-hidden="true"
      >
        <pattern
          id="grid"
          width="40"
          height="40"
          patternUnits="userSpaceOnUse"
        >
          <path
            d="M 40 0 L 0 0 0 40"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
          />
        </pattern>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
    </div>
  )
}
