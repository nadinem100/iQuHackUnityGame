using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor.Scripting.Python;
using UnityEditor;


public class second_btn_behavior : MonoBehaviour
{
    [MenuItem("Python Scripts/pythonconnector")]

	public static void pythonconnector()
	{
		PythonRunner.RunFile("Assets/second_py_script.py");
	}
}
