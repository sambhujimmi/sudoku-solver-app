import { StatusBar } from "expo-status-bar";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { Colors } from "./constants/Colors";
import SudokuGrid, { SudokuValue } from "./components/SudokuGrid";
import { useState } from "react";

export default function App() {
  const [initialValues, setInitialValues] = useState<
    SudokuValue[][] | undefined
  >(Array(9).fill(Array(9).fill(Math.random() > 0.5 ? "0" : "3")));

  function handleValueChange(row_id: number, col_id: number, value: string) {
    if (initialValues) {
      const newGrid = initialValues.map((row, i) =>
        row.map((cell, j) =>
          row_id === i && col_id === j ? (value as SudokuValue) : cell
        )
      );
      setInitialValues(newGrid);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.text}>Sudoku Solver</Text>
      <Pressable style={styles.button}>
        <Text style={{ color: Colors.light.text }}>Scan</Text>
      </Pressable>
      {initialValues ? (
        <SudokuGrid
          initialValues={initialValues}
          editable={true}
          onValueChange={handleValueChange}
        />
      ) : (
        <View></View>
      )}
      <StatusBar style="auto" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.dark.background,
    alignItems: "center",
    justifyContent: "center",
  },
  text: {
    color: Colors.dark.text,
  },
  button: {
    backgroundColor: Colors.dark.primary,
  },
});
