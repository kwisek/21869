import { useState } from "react";
import type { Sequence, SequenceCorrection } from "../../../../types/sequence";
import controlsStyles from '../../../../styles/modules/controls.module.scss';
import layoutStyles from '../../../../styles/modules/layout.module.scss';

type CorrectionFormProps = {
  correction: SequenceCorrection
  setSequence: (sequence: Sequence | null) => void;
  setCorrectionActive: (correctionActive: boolean) => void;
  applyCorrection: (correction: SequenceCorrection) => void;
};

function CorrectionForm(props: CorrectionFormProps) {

  const [correction, setCorrection] = useState<SequenceCorrection>({noteCount: 0, sequenceLength: 0});

  const updateNoteCount = (noteCount: number) => {
    setCorrection({noteCount: noteCount, sequenceLength: correction.sequenceLength});
  }

  const updateSequenceLength = (sequenceLength: number) => {
    setCorrection({noteCount: correction.noteCount, sequenceLength: sequenceLength});
  }

  const submitCorrection = () => {
    const correctionCopy: SequenceCorrection = {noteCount: correction.noteCount, sequenceLength: correction.sequenceLength};
    props.applyCorrection(correctionCopy);
    props.setSequence(null);
    props.setCorrectionActive(false);
  }

  return (
    <div className={layoutStyles.contentContainerCentered}>
      <div className={controlsStyles.controlsRow}>
        <center>
          <p>Liczba wykrytych nut</p>
          <p style={{fontSize: "0.75rem"}}>Czy liczba nut w każdym elemencie sekwencji była odpowiednia?</p>
          <div className={controlsStyles.inlineControlsContainer}>
            <div className={`${controlsStyles.inlineControl} ${correction.noteCount === -2 ? controlsStyles.active : ''}`} onClick={() => updateNoteCount(-2)}>Zdecydowanie za mała</div>
            <div className={`${controlsStyles.inlineControl} ${correction.noteCount === -1 ? controlsStyles.active : ''}`} onClick={() => updateNoteCount(-1)}>Za mała</div>
            <div className={`${controlsStyles.inlineControl} ${correction.noteCount === 0 ? controlsStyles.active : ''}`} onClick={() => updateNoteCount(0)}>Odpowiednia</div>
            <div className={`${controlsStyles.inlineControl} ${correction.noteCount === 1 ? controlsStyles.active : ''}`} onClick={() => updateNoteCount(1)}>Za duża</div>
            <div className={`${controlsStyles.inlineControl} ${correction.noteCount === 2 ? controlsStyles.active : ''}`} onClick={() => updateNoteCount(2)}>Zdecydowanie za duża</div>
          </div>
      </center>
      </div>
      
      <div className={controlsStyles.controlsRow} style={{marginTop: "2%"}}>
        <center>
          <p>Długość sekwencji:</p>
          <p style={{fontSize: "0.75rem"}}>Czy długość sekwencji nut była odpowiednia</p>
          <div className={controlsStyles.inlineControlsContainer}>
            <div className={`${controlsStyles.inlineControl} ${correction.sequenceLength === -2 ? controlsStyles.active : ''}`} onClick={() => updateSequenceLength(-2)}>Zdecydowanie za krótka</div>
            <div className={`${controlsStyles.inlineControl} ${correction.sequenceLength === -1 ? controlsStyles.active : ''}`} onClick={() => updateSequenceLength(-1)}>Za krótka</div>
            <div className={`${controlsStyles.inlineControl} ${correction.sequenceLength === 0 ? controlsStyles.active : ''}`} onClick={() => updateSequenceLength(0)}>Odpowiednia</div>
            <div className={`${controlsStyles.inlineControl} ${correction.sequenceLength === 1 ? controlsStyles.active : ''}`} onClick={() => updateSequenceLength(1)}>Za długa</div>
            <div className={`${controlsStyles.inlineControl} ${correction.sequenceLength === 2 ? controlsStyles.active : ''}`} onClick={() => updateSequenceLength(2)}>Zdecydowanie za długa</div>
          </div>
        </center>
      </div>


      <div className={controlsStyles.controlsRow} style={{marginTop: "2%"}}>
        <button className={`${controlsStyles.btnPrimary} ${controlsStyles.red}`} onClick={() => {props.setCorrectionActive(false)}}>Anuluj</button>
        
        <button className={`${controlsStyles.btnPrimary} ${controlsStyles.green}`} style={{marginTop: "2%"}} onClick={submitCorrection}>Wykonaj korektę</button>
      </div>
    </div>
  )
}

export default CorrectionForm;