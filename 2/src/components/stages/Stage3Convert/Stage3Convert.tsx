import { useEffect, useState } from 'react';
import { submitBlob } from '../../../services/convertService';
import { playNote } from '../../../services/soundService';
import controlsStyles from '../../../styles/modules/controls.module.scss';
import layoutStyles from '../../../styles/modules/layout.module.scss';
import styles from './Stage3Convert.module.scss';
import type { Sequence, SequenceCorrection, SequenceItem } from '../../../types/sequence';
import KalimbaLoader from '../../util/KalimbaLoader/KalimbaLoader';
import Stage from '../../../enums/Stage';
import Notation from '../../../enums/Notation';
import CorrectionForm from './CorrectionPopup/CorrectionForm';

type StageConvertProps = {
  setStage: (stage: Stage) => void;
  setSequence: (sequence: Sequence | null) => void;
  inputDataBlob: Blob;
  notation: Notation;
};

function StageConvert(props: StageConvertProps) {

  const [correction, setCorrection] = useState<SequenceCorrection>({noteCount: 0, sequenceLength: 0});
  const [localSequence, setLocalSequence] = useState<Sequence | null>(null);
  const [activeItemIndex, setActiveItemIndex] = useState<number | null>(null);
  const [correctionActive, setCorrectionActive] = useState<boolean>(false);

  const applyCorrection = async (corr: SequenceCorrection) => {

    const updatedCorrection = {noteCount: correction.noteCount + corr.noteCount, sequenceLength: correction.sequenceLength + corr.sequenceLength};
    setCorrection(updatedCorrection);
  
    const response = await submitBlob(props.inputDataBlob, updatedCorrection);
    setLocalSequence(response);

    console.log("Apply called, config is " + updatedCorrection.noteCount + ", " + updatedCorrection.sequenceLength);
  }

  useEffect(() => {
    setTimeout(async () => {
      const response = await submitBlob(props.inputDataBlob, correction);
      setLocalSequence(response);
    }, 1000);
  }, []);

  const playSequenceItem = async (item: SequenceItem, index: number) => {
    setActiveItemIndex(index);
    item.notes.forEach(note => playNote(note));

    await new Promise(resolve => setTimeout(resolve, 750));
    setActiveItemIndex(null);
  }

  const playSequence = async () => {
    if (localSequence) {

      for (let i = 0; i < localSequence.items.length; i++) {
        const item = localSequence.items[i];
        setActiveItemIndex(i);
        item.notes.forEach(note => playNote(note));

        await new Promise(resolve => setTimeout(resolve, 750));
      }
      setActiveItemIndex(null);
    }
  }

  const nextStage = () => {
    props.setStage(Stage.EDIT);
    props.setSequence(localSequence);
  }

  const getContentBasedOnNotation = (sequenceItem: SequenceItem): string => {
    const notes = sequenceItem.notes.map(note => props.notation === Notation.STANDARD ? note.standard : props.notation === Notation.NUMERIC ? note.numeric : note.letter).join(" ");
    return sequenceItem.notes.length > 1 ? `(${notes})` : notes;
  }

  return (  
    <div className={layoutStyles.contentContainerCentered}>

      {correctionActive && (
        <CorrectionForm correction={correction} setSequence={setLocalSequence} setCorrectionActive={setCorrectionActive} applyCorrection={applyCorrection} />
      )}

      {!correctionActive && (
        <>

          {localSequence === null && (
            <>
              <KalimbaLoader />
              <p>Trwa konwersja...</p>
            </>
          )}

          {localSequence !== null && (
            <>
              <center>
                <h2>Gotowe!</h2>
                <p>Sprawdź, czy wstępny rezultat spełnia Twoje oczekiwania. W kolejnym kroku będzie możliwa modyfikacja rezultatu.</p>
                <p>Jeśli nie, możesz nakazać systemowi spróbowanie ponownie, wyszukując więcej (lub mniej) nut.</p>
              </center>
              
              <div className={styles.sequenceContainer}>
                {localSequence.items.map((item, index) => (
                  <div key={index} className={`${styles.sequenceItemContainer} ${activeItemIndex === index ? styles.active : ''}`} onClick={() => playSequenceItem(item, index)}>
                    {getContentBasedOnNotation(item)}
                  </div>
                ))}
              </div>


              <div className={styles.controlsRow}>
                <button className={`${controlsStyles.btnPrimary} ${controlsStyles.red}`} onClick={() => setCorrectionActive(true)} disabled={activeItemIndex !== null}>&#10227; Wykonaj korektę</button>
                <button className={`${controlsStyles.btnPrimary} ${controlsStyles.blue}`} onClick={playSequence} disabled={activeItemIndex !== null}>&#9654; Odtwórz wszystkie</button>
                <button className={`${controlsStyles.btnPrimary} ${controlsStyles.green}`} onClick={nextStage}>&#10003; Zaakceptuj</button>
              </div>
            </>
          )}
        </>
      )}
     </div>
  )
}

export default StageConvert;