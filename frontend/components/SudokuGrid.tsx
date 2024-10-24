import { StyleSheet, TextInput, View } from "react-native";

export type SudokuValue =
  | ""
  | "0"
  | "1"
  | "2"
  | "3"
  | "4"
  | "5"
  | "6"
  | "7"
  | "8"
  | "9";
type Props = {
  initialValues: SudokuValue[][];
  editable: boolean;
  solutionValues?: SudokuValue[][];
  onValueChange?: (row_id: number, col_id: number, value: string) => void;
};

export default ({
  initialValues,
  editable,
  solutionValues,
  onValueChange,
}: Props) => {
  return (
    <View style={styles.container}>
      {initialValues.map((row, row_id) => (
        <View key={row_id} style={styles.row}>
          {row.map((cell, col_id) => {
            const bottomBorder = row_id % 3 === 2 && row_id < 8;
            const rightBorder = col_id % 3 === 2 && col_id < 8;
            return (
              <TextInput
                key={row_id + "-" + col_id}
                value={cell.toString()}
                maxLength={1}
                inputMode="numeric"
                keyboardType="numeric"
                editable={editable}
                style={[
                  styles.cell,
                  bottomBorder && styles.bottomBorder,
                  rightBorder && styles.rightBorder,
                ]}
                onChangeText={(text) =>
                  onValueChange ? onValueChange(row_id, col_id, text) : () => {}
                }
              />
            );
          })}
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 0,
    borderWidth: 3,
    borderColor: "#4b5563",
    backgroundColor: "#111827",
    flexDirection: "column",
    borderRadius: 10,
    elevation: 5,
  },
  row: {
    padding: 0,
    margin: 0,
    flexDirection: "row",
  },
  cell: {
    width: 35,
    fontSize: 25,
    margin: 0,
    color: "#93c5fd",
    aspectRatio: 1,
    borderWidth: 0.5,
    borderColor: "#4b5563",
    textAlign: "center",
  },
  bottomBorder: {
    borderBottomWidth: 3,
  },
  rightBorder: {
    borderRightWidth: 3,
  },
});
