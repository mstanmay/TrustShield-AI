import React from "react";
import { motion } from "framer-motion";

/**
 * TextReveal component that animates text word-by-word or character-by-character
 * with a viewport-triggered blur-to-sharp transition.
 */
export const TextReveal = ({
  text = "",
  as: Component = "p",
  splitBy = "words",
  staggerDelay = 0.05,
  duration = 0.5,
  once = true,
  blur = "12px",
  delay = 0,
  className = "",
  ...props
}) => {
  const MotionComponent = motion.create
    ? motion.create(Component)
    : motion[Component] || motion.div;

  const items = splitBy === "characters" ? text.split("") : text.split(" ");

  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: delay,
      },
    },
  };

  const childVariants = {
    hidden: {
      opacity: 0,
      filter: `blur(${blur})`,
      y: 12,
      scale: 0.96,
    },
    visible: {
      opacity: 1,
      filter: "none",
      y: 0,
      scale: 1,
      transition: {
        duration,
        ease: [0.25, 0.4, 0.25, 1],
      },
    },
  };

  return (
    <MotionComponent
      initial="hidden"
      whileInView="visible"
      viewport={{ once, margin: "-40px" }}
      variants={containerVariants}
      className={`inline-block ${className}`}
      {...props}
    >
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        const displayChar = item === " " ? "\u00A0" : item;

        return (
          <motion.span
            key={index}
            variants={childVariants}
            className="inline-block whitespace-pre"
          >
            {splitBy === "words" ? (
              <>
                {item}
                {!isLast && "\u00A0"}
              </>
            ) : (
              displayChar
            )}
          </motion.span>
        );
      })}
    </MotionComponent>
  );
};

export default TextReveal;
