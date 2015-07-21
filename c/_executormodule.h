#include <Python.h>

static PyObject* execute(PyObject* self, PyObject* args);
PyMODINIT_FUNC init_executor(void);

static PyMethodDef _executor_methods[] =
{
     {"execute", execute, METH_VARARGS, "Execute a Lua program, returning the result"},
     {NULL, NULL, 0, NULL}
};