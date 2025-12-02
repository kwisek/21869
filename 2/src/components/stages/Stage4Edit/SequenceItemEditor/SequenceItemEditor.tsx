import { Notes17, type NoteKey } from "../../../../types/noteKey";
import type { Sequence } from "../../../../types/sequence";
import styles from './SequenceItemEditor.module.scss';
import controlsStyles from '../../../../styles/modules/controls.module.scss';

type SequenceItemEditorProps = {
  sequence: Sequence;
  updateSequence: (sequence: Sequence) => void;
  editedItemIndex: number;
  setEditedItemIndex: (editedItemIndex: number | null) => void;
};

function SequenceItemEditor(props: SequenceItemEditorProps) {

  const orderedNoteSequence = () => {
    return [Notes17.D6, Notes17.B5, Notes17.G5, Notes17.E5, Notes17.C5, Notes17.A4, Notes17.F4, Notes17.D4, Notes17.C4, Notes17.E4, Notes17.G4, Notes17.B4, Notes17.D5, Notes17.F5, Notes17.A5, Notes17.C6, Notes17.E6];
  }

  const addNote = (note: NoteKey) => {
    const updatedSequence = { ...props.sequence };
    updatedSequence.items = [...updatedSequence.items];
    updatedSequence.items[props.editedItemIndex] = {...updatedSequence.items[props.editedItemIndex], notes: [...updatedSequence.items[props.editedItemIndex].notes, note]};
    props.updateSequence(updatedSequence);
  };

  const removeNote = (note: NoteKey) => {
    const updatedSequence = { ...props.sequence };
    updatedSequence.items = [...updatedSequence.items];
    updatedSequence.items[props.editedItemIndex] = {...updatedSequence.items[props.editedItemIndex], notes: updatedSequence.items[props.editedItemIndex].notes.filter(n => n !== note)};
    props.updateSequence(updatedSequence);
  };

  const isNotePresent = (note: NoteKey) => {
    return props.sequence.items[props.editedItemIndex].notes.includes(note);
  }

  const isBr = () => {
    return props.sequence.items[props.editedItemIndex].br;
  }

  const updateBr = (newBr: boolean) => {
    const updatedSequence = { ...props.sequence };
    updatedSequence.items = [...updatedSequence.items];
    updatedSequence.items[props.editedItemIndex] = {br: newBr, notes: updatedSequence.items[props.editedItemIndex].notes};
    props.updateSequence(updatedSequence);
  }

  const removeFromSequence = () => {
    const updatedSequence = { ...props.sequence };
    updatedSequence.items.splice(props.editedItemIndex, 1);
    props.updateSequence(updatedSequence);
    props.setEditedItemIndex(null);
  }

  const closeEditor = () => {
    if (props.sequence.items[props.editedItemIndex].notes.length === 0) {
      removeFromSequence();
    }
    props.setEditedItemIndex(null);
  }

  return (
    <>
      <div className={styles.sequenceItemEditorContainer}>
        {orderedNoteSequence().map(note => (
          <div key={note.standard} className={`${styles.sequenceItemEditorTile} ${isNotePresent(note) ? styles.active : ''}`} onClick={() => isNotePresent(note) ? removeNote(note) : addNote(note)}>{note.standard}</div>
        ))}
      </div>
      <div className={styles.controlsRow}>
        <div className={`${styles.sequenceItemEditorTile} ${styles.brIndicator} ${isBr() ? styles.active : ''}`} onClick={() => updateBr(!isBr())}>
          <center>Koniec linii</center>
        </div>
      </div>
      <div className={styles.controlsRow}>
        <button className={`${controlsStyles.btnPrimary} ${controlsStyles.red}`} onClick={removeFromSequence}>&#128465; Usuń z sekwencji</button>
        <button className={`${controlsStyles.btnPrimary} ${controlsStyles.green}`} onClick={closeEditor}>&#10003; Zaakceptuj</button>
      </div>
    </>
  )
}

export default SequenceItemEditor;