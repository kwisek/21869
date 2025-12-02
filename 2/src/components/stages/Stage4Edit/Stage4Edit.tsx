import { useState } from 'react';
import type { Sequence, SequenceItem } from '../../../types/sequence';
import controlsStyles from '../../../styles/modules/controls.module.scss';
import layoutStyles from '../../../styles/modules/layout.module.scss';
import styles from './Stage4Edit.module.scss';
import { playNote } from '../../../services/soundService';
import Stage from '../../../enums/Stage';
import SequenceItemWrapper from './SequenceItemWrapper/SequenceItemWrapper';
import ClickingBehavior from '../../../enums/ClickingBehavior';
import SequenceItemEditor from './SequenceItemEditor/SequenceItemEditor';
import Notation from '../../../enums/Notation';
import { Notes17, type NoteKey } from '../../../types/noteKey';

type StageEditProps = {
  sequence: Sequence;
  notation: Notation;
  setSequence: (sequence: Sequence) => void;
  setStage: (stage: Stage) => void;
};

function StageEdit(props: StageEditProps) {

  const sequenceToText = (sequence: Sequence): string => {
    return sequence.items.map(item => {
      const notes = item.notes.map(note => {
        switch (props.notation) {
          case Notation.NUMERIC:
            return note.numeric;
          case Notation.LETTERED:
            return note.letter;
          case Notation.STANDARD:
          default:
            return note.standard;
        }
      });

      return (notes.length === 1  ? notes[0] : `(${notes.join(" ")})`) + (item.br ? '\n' : '');
    }).join(" ").replace("\n ", '\n');
  }

  const textToSequence = (text: string, notation: Notation): Sequence => {
    const findNote = (token: string) =>
      Object.values(Notes17).find(n =>
        notation === Notation.STANDARD ? n.standard === token
        : notation === Notation.NUMERIC ? n.numeric === token
        : n.letter === token
      );

    text = text.replace(/\s+\n/g, '\n');

    const items: SequenceItem[] = [];
    let depth = 0, current = '';

    for (let i = 0; i <= text.length; i++) {
      const char = text[i] || ',';
      if (char === '(') depth++;
      if (char === ')') depth--;

      if ((char === ' ' && depth === 0) || i === text.length || char === '\n') {
        const trimmed = current.trim();
        if (trimmed) {
          const inner = trimmed.startsWith('(') && trimmed.endsWith(')') ? trimmed.slice(1, -1) : trimmed;
          const notes = inner.split(/\s+/).map(t => findNote(t)).filter(Boolean) as NoteKey[];
          if (notes.length) {
            items.push({ br: char === '\n', notes: notes });
          }
        }
        current = '';
      } else {
        current += char;
      }
    }

    return { items };
  };

  const [highlightedItemIndex, setHighlightedItemIndex] = useState<number | null>(null);
  const [editedItemIndex, setEditedItemIndex] = useState<number | null>(null);
  const [onClickBehavior, setOnClickBehavior] = useState<ClickingBehavior>(ClickingBehavior.PLAYING);
  const [rawSequence, setRawSequence] = useState<string>(sequenceToText(props.sequence));

  const updateSequence = (newSequence: Sequence) => {
    props.setSequence(newSequence);
    setRawSequence(sequenceToText(newSequence));
  }

  function onRawSequenceChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    const newText = e.target.value;
    setRawSequence(newText);
    const parsed = textToSequence(newText, props.notation);
    props.setSequence(parsed);
  }

  const playSequence = async () => {
    for (let i = 0; i < props.sequence.items.length; i++) {
      const item = props.sequence.items[i];
      setHighlightedItemIndex(i);
      item.notes.forEach(note => playNote(note));

      await new Promise(resolve => setTimeout(resolve, 750));
    }
    setHighlightedItemIndex(null);
  }

  const insertItem = (index: number) => {
    const newItem: SequenceItem = {br: false, notes: []};
    const newItems = [...props.sequence.items.slice(0, index), newItem, ...props.sequence.items.slice(index)];
    updateSequence({ ...props.sequence, items: newItems });
  };

  const nextStage = () => {
    props.setStage(Stage.EXPORT);
  }

  return (  
    <div className={layoutStyles.contentContainerCentered}>

      <center>
        <p>W przypadku niedoskonałości, dokonaj korekty.</p>
        <p>System umożliwia pracę w trzech trybach: Odsłuch (odtwarzanie nut), Edycja interaktywna (przyciski), Edycja tekstowa (bezpośrednia modyfikacja nut).</p>
      </center>

      {editedItemIndex !== null && (
        <SequenceItemEditor sequence={props.sequence} updateSequence={updateSequence} editedItemIndex={editedItemIndex} setEditedItemIndex={setEditedItemIndex} />
      )}

      {editedItemIndex === null && (
        <>
          <div className={styles.controlsRow} style={{marginBottom: "5%"}}>
            <p>Tryb pracy: </p>
            <div className={controlsStyles.inlineControlsContainer}>
              <div className={`${controlsStyles.inlineControl} ${onClickBehavior === ClickingBehavior.PLAYING ? controlsStyles.active : ''}`} onClick={() => setOnClickBehavior(ClickingBehavior.PLAYING)}>Odsłuch</div>
              <div className={`${controlsStyles.inlineControl} ${onClickBehavior === ClickingBehavior.EDITING ? controlsStyles.active : ''}`} onClick={() => setOnClickBehavior(ClickingBehavior.EDITING)}>Edycja (interaktywna)</div>
              <div className={`${controlsStyles.inlineControl} ${onClickBehavior === ClickingBehavior.EDITING_RAW ? controlsStyles.active : ''}`} onClick={() => setOnClickBehavior(ClickingBehavior.EDITING_RAW)}>Edycja (tekstowa)</div>
            </div>
          </div>

          {(onClickBehavior === ClickingBehavior.EDITING || onClickBehavior === ClickingBehavior.PLAYING) && (
            <>
              <div className={styles.sequenceContainer}>
                {props.sequence.items.map((item, index) => (
                  <>
                    {onClickBehavior === ClickingBehavior.EDITING && (
                      <div key={index + "-ph"} className={styles.sequenceInsertionSlot} onClick={() => {insertItem(index)}}>+</div>
                    )}
                    <SequenceItemWrapper key={index + "-it"} sequenceItem={item} index={index} notation={props.notation} onClickBehavior={onClickBehavior} activeItemIndex={highlightedItemIndex} setHighlightedItemIndex={setHighlightedItemIndex} setEditedItemIndex={setEditedItemIndex} />
                    {item.br && (<div className={styles.flexBreak}/>)}
                  </>
                ))}
                
                {onClickBehavior === ClickingBehavior.EDITING && (
                  <div key={props.sequence.items.length + "-ph"} className={styles.sequenceInsertionSlot} onClick={() => {insertItem(props.sequence.items.length)}}>+</div>
                )}
              </div>
            </>
          )}
          {onClickBehavior === ClickingBehavior.EDITING_RAW && (
            <textarea className={styles.rawSequenceWrapper} value={rawSequence} onChange={onRawSequenceChange} />
          )}

          <div className={styles.controlsRow}>
            <button className={`${controlsStyles.btnPrimary} ${controlsStyles.blue}`} onClick={playSequence} disabled={highlightedItemIndex !== null}>&#9654; Odtwórz wszystkie</button>
            <button className={`${controlsStyles.btnPrimary} ${controlsStyles.green}`} onClick={nextStage}>&#10003; Zaakceptuj</button>
          </div>
        </>
      )}
    </div>
  )
}

export default StageEdit;