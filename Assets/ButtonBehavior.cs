using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor.Scripting.Python;
using UnityEditor;


public class ButtonBehavior : MonoBehaviour
{
	public static int winner;
	public static ArrayList circuit_data1 = new ArrayList();
  public static ArrayList circuit_data2 = new ArrayList();

	[MenuItem("Python Scripts/pythonconnector")]
	public static void pythonconnector()
	{

		PythonRunner.RunFile("Assets/new_python_script.py");
	}

	public static void process_pl1() {
		string gate1 = GameObject.Find("Dropdown1").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string pos1 = GameObject.Find("Dropdown_Land1").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string gate2 = GameObject.Find("Dropdown2").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string pos2 = GameObject.Find("Dropdown_Land2").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string gate3 = GameObject.Find("Dropdown3").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string pos3 = GameObject.Find("Dropdown_Land3").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
		
		// circuit_data1.Add(new ArrayList(){gate_translate(gate1), pos_translate(pos1)});
		// circuit_data1.Add(new ArrayList(){gate_translate(gate2), pos_translate(pos2)});
		// circuit_data1.Add(new ArrayList(){gate_translate(gate3), pos_translate(pos3)});
		
		GameObject.Find("Dropdown1").GetComponent<UnityEngine.UI.Dropdown>().value = 0;
		GameObject.Find("Dropdown_Land1").GetComponent<UnityEngine.UI.Dropdown>().value = 0;
		GameObject.Find("Dropdown2").GetComponent<UnityEngine.UI.Dropdown>().value = 0;
		GameObject.Find("Dropdown_Land2").GetComponent<UnityEngine.UI.Dropdown>().value = 0;
		GameObject.Find("Dropdown3").GetComponent<UnityEngine.UI.Dropdown>().value = 0;
		GameObject.Find("Dropdown_Land3").GetComponent<UnityEngine.UI.Dropdown>().value = 0;

		string[] arr = {gate1, pos1, gate2, pos2, gate3, pos3};

		GameObject.Find("InvisibleText1").GetComponent<UnityEngine.UI.Text>().text = string.Join(" ", arr);

	}

	public static void process_pl2() {
		string gate1 = GameObject.Find("Dropdown1").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string pos1 = GameObject.Find("Dropdown_Land1").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string gate2 = GameObject.Find("Dropdown2").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string pos2 = GameObject.Find("Dropdown_Land2").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string gate3 = GameObject.Find("Dropdown3").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
    string pos3 = GameObject.Find("Dropdown_Land3").GetComponent<UnityEngine.UI.Dropdown>().value.ToString();
		
		// circuit_data2.Add(new ArrayList(){gate_translate(gate1), pos_translate(pos1)});
		// circuit_data2.Add(new ArrayList(){gate_translate(gate2), pos_translate(pos2)});
		// circuit_data2.Add(new ArrayList(){gate_translate(gate3), pos_translate(pos3)});

		string[] arr = {gate1, pos1, gate2, pos2, gate3, pos3};
		GameObject.Find("InvisibleText2").GetComponent<UnityEngine.UI.Text>().text = string.Join(" ", arr);
	}

	public static string gate_translate(int index) {
		if (index == 0) return "X";
		if (index == 1) return "H";
		if (index == 2) return "S";
		if (index == 3) return "CX";
		if (index == 4) return "I";
		return "BYE";
  }

	public static ArrayList pos_translate(int index) {
		if (index < 2) {
				return new ArrayList(){index};
		}
		else if (index == 2) {
				return new ArrayList(){0 ,1};
		} else {
				return new ArrayList(){1, 0};
		}
	}
    // 0: X, 1:?


}
