import { StatusBar } from "expo-status-bar";
import {
  Button,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { Colors } from "./constants/Colors";

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.text}>Sudoku Solver</Text>
      <Pressable style={styles.button}>
        <Text style={{ color: Colors.light.text }}>Scan</Text>
      </Pressable>
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
