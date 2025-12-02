import Notation from "../../../enums/Notation";
import Stage from "../../../enums/Stage";
import { toImage, toPdf } from "../../../services/exportService";
import controlsStyles from '../../../styles/modules/controls.module.scss';
import layoutStyles from '../../../styles/modules/layout.module.scss';
import type { Sequence } from "../../../types/sequence";
import styles from "./Stage5Export.module.scss";

type StageExportProps = {
  setStage: (stage: Stage) => void;
  notation: Notation;
  sequence: Sequence
};

function StageExport(props: StageExportProps) {
  

  const triggerImageExport = () => {
    toImage(props.sequence, props.notation)
  }

  const triggerPdfExport = () => {
    toPdf(props.sequence, props.notation);
  }

  const sequenceToText = (): string => {
    return props.sequence.items.map(item => {
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
  };

  return (
    <div className={layoutStyles.contentContainerCentered}>

      <center>
        <h2>Eksport gotowy</h2>
      </center>

      <div className={styles.controlsRow}>
        <button className={`${controlsStyles.btnPrimary} ${controlsStyles.green}`} onClick={triggerImageExport}>Pobierz png</button>
        <button className={`${controlsStyles.btnPrimary} ${controlsStyles.green}`} onClick={triggerPdfExport}>Pobierz pdf</button>
      </div>

      <div className={styles.controlsRow}>
        <p>Lub skopiuj tekst poniżej</p>
      </div>

      <textarea className={styles.sequenceContainer} readOnly disabled value={sequenceToText()} />
      
      <div className={styles.controlsRow}>
        <button className={`${controlsStyles.btnPrimary} ${controlsStyles.blue}`} onClick={() => props.setStage(Stage.START)}>Rozpocznij od nowa</button>
      </div>
    </div>
  );
}

export default StageExport;