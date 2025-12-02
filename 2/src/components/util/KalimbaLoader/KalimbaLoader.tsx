import { useEffect, useState } from "react";
import styles from "./KalimbaLoader.module.scss";

class NoteIcon {
  id: number;
  x: number;
  y: number;
  color: string;

  constructor(id: number, x: number, y: number, color: string) {
    this.id = id;
    this.x = x;
    this.y = y;
    this.color = color;
  }
}

function KalimbaLoader() {

  let noteId = 0;

  const tilePositions = [50, 140, 230, 320, 410];
  const tileHeights = [250, 270, 300, 280, 260];
  const colors = ["#FF5722", "#FFC107", "#4CAF50", "#03A9F4"];

  const [highlightedTile, setHighlightedTile] = useState<number | null>(null);
  const [highlightColor, setHighlightColor] = useState<string>(colors[0]);
  
  const [notes, setNotes] = useState<NoteIcon[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const randomTile = Math.floor(Math.random() * 5);
      const randomColor = colors[Math.floor(Math.random() * colors.length)];

      setNotes((prev) => [...prev, new NoteIcon(noteId++, tilePositions[randomTile], 250, randomColor)]);
      setHighlightColor(randomColor);
      setHighlightedTile(randomTile);

      setTimeout(() => {
        setHighlightedTile(null);
      }, 500);
    }, 1500);
      
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let animationFrame: number;

    const animate = () => {
      setNotes((prev) => prev.map((note) => ({ ...note, y: note.y - 2 })).filter((note) => note.y > 0));
      animationFrame = requestAnimationFrame(animate);
    };

    animationFrame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrame);
  }, []);

  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="5%" height="5%" viewBox="0 0 500 1000" className={styles.kalimbaLoader}>

      <rect x="0" y="300" width="500" height="700" fill="none" stroke="#e0e0e0" rx="75" ry="75" strokeWidth="10"  />

      {tilePositions.map((x, i) => (
        <rect key={i} x={x} y="350" width="40" height={tileHeights[i]} rx="10" ry="10" fill={highlightedTile === i ? highlightColor : "#e0e0e0"}/>
      ))}

      {notes.map((note) => (
        <text key={note.id} x={note.x} y={note.y} fontSize="1000%" fill={note.color}>&#9834;</text>
      ))}

      <circle cx="250" cy="800" r="75" fill="#e0e0e0" />
    </svg>
  );
}

export default KalimbaLoader;
