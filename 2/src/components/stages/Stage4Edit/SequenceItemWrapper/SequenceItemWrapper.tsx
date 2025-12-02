import ClickingBehavior from "../../../../enums/ClickingBehavior";
import Notation from "../../../../enums/Notation";
import { playNote } from "../../../../services/soundService";
import type { SequenceItem } from "../../../../types/sequence";
import styles from './SequenceItemWrapper.module.scss';

type SequenceItemWrapperProps = {
  sequenceItem: SequenceItem;
  index: number;
  notation: Notation;
  activeItemIndex: number | null;
  setHighlightedItemIndex: (index: number | null) => void;
  setEditedItemIndex: (index: number | null) => void;
  onClickBehavior: ClickingBehavior;
};

function SequenceItemWrapper(props: SequenceItemWrapperProps) {

  const isHighlighted = () => {
    return props.index === props.activeItemIndex;
  }

  const getContentBasedOnNotation = (): string => {
    const notes = props.sequenceItem.notes.map(note => props.notation === Notation.STANDARD ? note.standard : props.notation === Notation.NUMERIC ? note.numeric : note.letter).join(" ");
    return props.sequenceItem.notes.length > 1 ? `(${notes})` : notes;
  }

  const handleClick = async () => {
    if (props.onClickBehavior === ClickingBehavior.PLAYING) {
        props.setHighlightedItemIndex(props.index);
        props.sequenceItem.notes.forEach(note => playNote(note));
        await new Promise(resolve => setTimeout(resolve, 750));
        props.setHighlightedItemIndex(null);
    }
    else if (props.onClickBehavior === ClickingBehavior.EDITING) {
      props.setEditedItemIndex(props.index);
    }
  }

  return (
    <>
      <div key={props.index} className={`${styles.sequenceItemContainer} ${isHighlighted() ? styles.active : ''}`}>
          <div key={props.index + "-overlay"} className={`${styles.sequenceItemOverlay} ${styles.left}`} onClick={handleClick}>
            {props.onClickBehavior === ClickingBehavior.EDITING && <p>&#9881;</p>}
            {props.onClickBehavior === ClickingBehavior.PLAYING && <p>&#9654;</p>}
          </div>
          {getContentBasedOnNotation()}
      </div>
    </>
  );
}

export default SequenceItemWrapper;