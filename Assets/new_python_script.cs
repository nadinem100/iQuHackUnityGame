using UnityEditor;
using UnityEditor.Scripting.Python;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MenuItem_pythonconnector_Class
{
   [MenuItem("Python Scripts/pythonconnector")]
   public static void pythonconnector()
   {
       PythonRunner.RunFile("Assets/new_python_script.py");
       }
};
