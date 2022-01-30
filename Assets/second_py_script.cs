using UnityEditor;
using UnityEditor.Scripting.Python;

public class MenuItem_second_py_script_Class
{
   [MenuItem("Python Scripts/second_py_script")]
   public static void second_py_script()
   {
       PythonRunner.RunFile("Assets/second_py_script.py");
       }
};
