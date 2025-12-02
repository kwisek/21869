import type Stage from '../../../enums/Stage';
import styles from './StateBar.module.scss';

const color1 = "#a0a0a0";
const color2 = "#78bfb9";
const color3 = "#00aea1";

type StateBarProps = {
  stage: Stage;
};

function StateBar(props: StateBarProps) {

  const bgForItem = (idx: number): string => {
    return props.stage < idx ? color1 : props.stage == idx ? color3 : color2;
  }

  return (
    <div className={styles.stateBarContainer}>
      <div className={styles.stateBarItem} style={{backgroundColor: bgForItem(0)}}>Start</div>
      <div className={styles.stateBarItem} style={{backgroundColor: bgForItem(1)}}>Źródło</div>
      <div className={styles.stateBarItem} style={{backgroundColor: bgForItem(2)}}>Konwersja</div>
      <div className={styles.stateBarItem} style={{backgroundColor: bgForItem(3)}}>Edycja</div>
      <div className={styles.stateBarItem} style={{backgroundColor: bgForItem(4)}}>Eksport</div>
    </div>
  );
}



export default StateBar;
