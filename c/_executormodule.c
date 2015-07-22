#include <stdlib.h>
#include <stdio.h>

#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

#include <Python.h>

#include "_executormodule.h"

/*
 * the libraries require about 100k to run, but if we don't install tjhem we can
 * get by with about 10k
 */
const size_t MAX_LUA_ALLOCATION=500*1024;
const size_t MAX_LUA_EXECUTION=100000;
const size_t MAX_LUA_DEPTH=10;

struct custom_alloc_data {
    size_t limit;
    size_t used;
};

#define abs_index(L, i) ((i) > 0 || (i) <= LUA_REGISTRYINDEX ? (i) : \
                                       lua_gettop(L) + (i) + 1)

void stackDump(lua_State *L) {
    int i;
    int top = lua_gettop(L);
    for (i = 1; i <= top; i++) {  /* repeat for each level */
        int t = lua_type(L, i);

        switch (t) {

        case LUA_TSTRING:  /* strings */
                printf("`%s'", lua_tostring(L, i));
                break;

        case LUA_TBOOLEAN:  /* booleans */
            printf(lua_toboolean(L, i) ? "true" : "false");
            break;

        case LUA_TNUMBER:  /* numbers */
            printf("%g", lua_tonumber(L, i));
            break;

        default:  /* other values */
            printf("%s", lua_typename(L, t));
            break;

        }
        printf("  ");  /* put a separator */
    }
    printf("\n");  /* end the listing */
}


void* l_alloc_restricted (void *ud, void *ptr, size_t osize, size_t nsize) {
   struct custom_alloc_data* alloc_data = (struct custom_alloc_data*)ud;

    if (nsize == 0) {
        free(ptr);
        alloc_data->used -= osize; /* subtract old size from used memory */
        return NULL;
    }

    if (alloc_data->used + (nsize - osize) > alloc_data->limit) {
        /* too much memory in use */
        return NULL;
    }

    ptr = realloc(ptr, nsize);
    if (ptr) {
        /* reallocation successful */
        alloc_data->used += (nsize - osize);
    }

    return ptr;
}

void time_limiting_hook(lua_State *L, lua_Debug *ar) {
    lua_pushstring(L, "time quota exceeded");
    lua_error(L);
}

int encode_python_to_lua(lua_State* L, PyObject* value, int recursion) {
    if(recursion > 10) {
        PyErr_SetString(PyExc_RuntimeError, "encode_python_to_lua recursed too far");
        return 0;

    } else if(!lua_checkstack(L, 1)) {
        PyErr_SetString(PyExc_TypeError, "not enough lua stack space");
        return 0;

    } else if(value == Py_None) {
        lua_pushnil(L);

    } else if(PyBool_Check(value)) {
        if(value == Py_False) {
            lua_pushboolean(L, 0);
        } else {
            lua_pushboolean(L, 1);
        }

    } else if(PyInt_Check(value)) {
        long as_long = PyInt_AsLong(value);

        if(PyErr_Occurred()) {
            return 0;
        }

        lua_pushnumber(L, (double)as_long);

    } else if(PyLong_Check(value)) {
        long as_long = PyLong_AsLong(value);

        if(PyErr_Occurred()) {
            return 0;
        }

        lua_pushnumber(L, (double)as_long);

    } else if(PyFloat_Check(value)) {
        double as_double = PyFloat_AsDouble(value);

        if(PyErr_Occurred()) {
            return 0;
        }

        lua_pushnumber(L, as_double);

    } else if(PyString_Check(value)) {
        char* body = NULL;
        Py_ssize_t len = 0;

        if(PyString_AsStringAndSize(value, &body, &len)==-1) {
            return 0;
        }

        lua_pushlstring(L, body, len);

    } else if(PyDict_Check(value)) {
        lua_newtable(L);

        PyObject *dkey, *dvalue;
        Py_ssize_t pos = 0;

        while (PyDict_Next(value, &pos, &dkey, &dvalue)) {
            /*
             * serialize the key and value and leave them on the lua stack. if
             * either of these fail, they'll leave their error on the python
             * stack and return false
             */

            /*
             * To put values into the table, we first push the index, then the
             * value, and then call lua_rawset() with the index of the table in the
             * stack. Let's see why it's -3: In Lua, the value -1 always refers to
             * the top of the stack. When you create the table with lua_newtable(),
             * the table gets pushed into the top of the stack. When you push the
             * index and then the cell value, the stack looks like:
             *
             * <- [stack bottom] -- table, index, value [top]
             *
             * So the -1 will refer to the cell value, thus -3 is used to refer to
             * the table itself. Note that lua_rawset() pops the two last elements
             * of the stack, so that after it has been called, the table is at the
             * top of the stack.
             */

            if(!encode_python_to_lua(L, dkey, recursion+1)) {
                return 0;
            }
            if(!encode_python_to_lua(L, dvalue, recursion+1)) {
                return 0;
            }

            /* lua will pop off the key and value now, leaving only the table */
            lua_settable(L, -3);
        }


    } else {
        PyErr_SetString(PyExc_TypeError, "cannot serialize unknown python type");
        return 0;
    }

    return 1;
}

int serialize_python_to_lua(lua_State* L, PyObject* env) {
    /*
     * take a lua_State and a Python Dict and encode that dict into global
     * variables in Lua. If this fails, it may leave the Lua stack in a bad way,
     * but we'll consider that okay because we'll dispose of it anyway
     */

    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(env, &pos, &key, &value)) {
        if(!PyString_Check(key)) {
            /* TODO: put the key in the error message */
            PyErr_SetString(PyExc_TypeError, "key must be str");
            return 0;
        }

        char* keystring = NULL;

        /* length is null to disallow \0 bytes */
        if(PyString_AsStringAndSize(key, &keystring, NULL)==-1) {
            return 0;
        }

        if(!encode_python_to_lua(L, value, 0)) {
            /* will have an exception on the python stack */
            return 0;
        }

        /* now the value is on the stack, save it to the global variable */
        lua_setglobal(L, keystring);
    }

    return 1;
}

PyObject* serialize_lua_to_python(lua_State* L, int idx, int recursion) {
    /*
     * like serialize_python_to_lua, we can leave the Lua stack in a bad way,
     * but we declare this to be okay because we'll destroy it anyway. however,
     * we will not leave the Python state in any bad state (other than
     * potentially an exception set), as we are returning to Python afterwards
     */
    PyObject* ret = NULL;

    double as_double;
    int as_boolean;

    /* convert to absolute index because we'll mess with the stack */
    idx = abs_index(L, idx);

    if(recursion > 10) {
        PyErr_SetString(PyExc_RuntimeError, "serialize_lua_to_python recursed too far");
        return NULL;
    }

    switch(lua_type(L, idx)) {

    case LUA_TNIL:
        ret = Py_None;
        Py_INCREF(ret);
        break;

    case LUA_TNUMBER:
        as_double = lua_tonumber(L, idx);
        ret = PyFloat_FromDouble(as_double);
        if(ret == NULL) {
            return NULL;
        }
        break;

    case LUA_TBOOLEAN:
        as_boolean = lua_toboolean(L, idx);
        if(as_boolean) {
            ret = Py_True;
        } else {
            ret = Py_False;
        }
        Py_INCREF(ret);
        break;

    case LUA_TSTRING:
        ret = PyString_FromStringAndSize(lua_tostring(L, idx),
                                         lua_rawlen(L, idx));
        if(ret==NULL) {
            return NULL;
        }
        break;

    case LUA_TTABLE:
        /* the complex case */
        ret = PyDict_New();

        if(ret == NULL) {
            return NULL;
        }

        int table_index = abs_index(L, idx);

        lua_pushnil(L);  /* first key */

        while (lua_next(L, table_index) != 0) {
            /* `key' is at index -2 and `value' at index -1 */
            PyObject* key = serialize_lua_to_python(L, -2, recursion+1);
            if(key == NULL) {
                Py_DECREF(ret);
                return NULL;
            }

            PyObject* value = serialize_lua_to_python(L, -1, recursion+1);
            if(value == NULL) {
                Py_DECREF(key);
                Py_DECREF(ret);
                return NULL;
            }

            if(!PyDict_SetItem(ret, key, value) == -1) {
                Py_DECREF(key);
                Py_DECREF(value);
                Py_DECREF(ret);
                return NULL;
            }

            /* now the dictionary owns them */
            Py_DECREF(key);
            Py_DECREF(value);

            lua_pop(L, 1);  /* removes `value'; keeps `key' for next iteration */
        }

        break;

    default:
        PyErr_SetString(PyExc_RuntimeError, "cannot serialize unknown Lua type");
        return NULL;
    }

    return ret;
}

static PyObject* execute(PyObject* module, PyObject* args) {
    PyObject* env;
    PyObject* pyresult;

    char* program_code = NULL;
    size_t program_len = 0;

    if(!PyArg_ParseTuple(args, "s#O!",
                         &program_code, &program_len,
                         &PyDict_Type, &env)) {
        return NULL;
    }

    struct custom_alloc_data alloc_data = {MAX_LUA_ALLOCATION, 0};

    /*
     * All Lua contexts are held in this structure. We work with it almost
     * all the time.
     */
    lua_State *L = lua_newstate(l_alloc_restricted, &alloc_data);

    /*
     * Load Lua libraries. We go ahead and load them all up here, but in
     * sandbox.lua we limit what can actually be called
     */
    luaL_openlibs(L);

    /* install our time-limiting hook */
    lua_sethook(L, time_limiting_hook, LUA_MASKCOUNT, MAX_LUA_EXECUTION);

    /* if we got an environment to pass in, translate it from Python to Lua */
    if(PyDict_Size(env)>=0 && !serialize_python_to_lua(L, env)) {
        /* there will be an error on the Python stack */
        goto done;
    }

    /* Load the the script we are going to run */
    if (luaL_loadbufferx(L, program_code, program_len, "sandboxer", "t")) {
        /* If something went wrong, error message is at the top of the stack */

        /* copy the errstring out into a Python string */
        PyObject* pyerrstring = PyString_FromStringAndSize(lua_tostring(L, -1),
                                                           lua_rawlen(L, -1));
         if(!pyerrstring) {
            goto done;
        }

        PyErr_SetObject(PyExc_RuntimeError, pyerrstring);

        goto done;
    }

    int stack_top_before = lua_gettop(L);
    int lua_result;

    Py_BEGIN_ALLOW_THREADS;

    /* Ask Lua to run our script */
    lua_result = lua_pcall(L, 0, LUA_MULTRET, 0);

    Py_END_ALLOW_THREADS;

    if(lua_result != LUA_OK) {
        /* If something went wrong, error message is at the top of the stack */

        /* copy the errstring out */
        PyObject* pyerrstring = PyString_FromStringAndSize(lua_tostring(L, -1),
                                                           lua_rawlen(L, -1));
         if(!pyerrstring) {
            goto done;
        }

        PyErr_SetObject(PyExc_RuntimeError, pyerrstring);

        goto done;
    }

    /*
     * lua removes from the stack the code chunk that we loaded and the
     * arguments to it (which we didn't pass), and leaves the return values on
     * it afterwards.
     * if there was an error, it's signalled in lua_result and the error message
     * left instead. in that case, we'll extract it and return NULL and leave an
     * exception on the Python stack
     */

    int stack_top_after = lua_gettop(L);
    int results_returned = 1+stack_top_after-stack_top_before;

    pyresult = PyTuple_New(results_returned);

    if(pyresult==NULL) {
        goto done;
    }

    if(results_returned==0) {
        // success, return the empty tuple
        goto done;
    }

    for(int i=0; i<results_returned; i++) {
        int stacknum = stack_top_before+i;
        PyObject* thisresult = serialize_lua_to_python(L, stacknum, 0);
        if(thisresult==NULL) {
            Py_DECREF(pyresult);
            goto done;
        }
        // steals the thisresult ref
        if(PyTuple_SetItem(pyresult, i, thisresult)==-1) {
            Py_DECREF(pyresult);
            goto done;
        }
    }
    lua_pop(L, results_returned);

done:
    lua_close(L);

    if(PyErr_Occurred()) {
        return NULL;
    }

    return pyresult;
}

PyMODINIT_FUNC init_executor(void) {
     (void)Py_InitModule("_executor", _executor_methods);
}
