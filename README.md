# pyawk

This module supplies the base functionality of awk to python3 programs, and is an updated version of the earlier pyawk program which was written at the turn of the century
.
The name awk comes from the initials of its designers: Alfred V. Aho Peter
J. Weinberger, and brian W. Hernighan. The original version of awk was
written in 1977. Since then there have been several versions nawk, gawk
etc.

This module contains an awk like processor. The basic idea is taken
from awk, but the scripting language is python. To put it another way,
the script file contains python blocks, and the regular expression patterns
are python regular expressions as parsed by the re module.&nbsp;

This module can be used in the many ways that awk can:

* Extract information from text files.
* Generate reports&nbsp;</li>
* Perform documentation preparation tasks. etc, etc

The pyawk module can be used in three ways:

- For normal awk like processing:
  ```
  python pyawk.py -f script data
  ```
- Called as a function:
  ```
  pyawk.pyawk(scriptfile,&nbsp; datafile, ';')
  ```
- Embedded in an application as an object:
  ```
  AwkProcessor = pyawk.PyAwk( Script, ';')
  Output = AwkProcessor.Run(Data)
  ```
  
If you are already familiar with awk, watch out there are many differences,
as most of the awk syntax has been replaced by python syntax. Probably
the biggest difference is that pyawk will be much slower than awk which
is compiled and not interpreted. Having said that, I have found pyawk quite
adequate for use with small to medium data file sizes.&nbsp;

As time permits, I plan to implement some of the unimplemented features,
if you need a particular feature, please feel free to contact me at roger.wenham@gmx.net
and I will move it to the top of the todo list.

## Pyawk Syntax
The following is a brief overview of pyawk with a comparison to the
original awk functionality.

### Initialisation
  ```
  pyawk(Script, Data=None, FiledSep=' ', Decl=None)
  ```  
where...
- Script 
  + This is the file containing the pyawk program (awk -f option)
- Data 
  + This is the name of the file containing the data that the Program will operate on. This may be None.
- FieldSep 
  + The field separator (awk -F option) defaults to '&nbsp; '
- Decl 
  + A dictionary containing variable definitions: Var=Value that will be available in the local namespace when the program runs. (awk -v option)

### Program file format
  ```
  /pattern/ {
  python statements
  }
  ```
**Note:**
*Unlike awk, the python program statements
start on the next line, and are indent formatted in the normal python style.*

The trailing bracket must be in the first column on a line by itself.
  ```
  function(parameter list) {
    python statements ......
  }
  ```
Not yet implemented.

### Fields
As python variables cannot start with a '$', I have used an underscore
istead. For example _0 contains the input line being processes, and _2
contains the second field of that line, if it exists.

References to non existant fields will cause an exception, and will
not be created as they are in awk.

| AWK | PYAWK | Explanation |
| :--- | :----- | :----------- |
| $0 | _0 | The whole (unsplit) matched line |
| $1...$n | _1..._n | The individual fields that the line has been split into. |
| | _ | The fields as a python list ([_0..._n]) There is no equivalent in awk. |

### Parameters
Parameters are available in the namespace at runtime.

| AWK | PYAWK | Explanation |
| :--- | :----- | :----------- |
| ARGC | sys.argc | The number of command line arguments. |
| ARGV | sys.argv | The array of command line arguments. | 
| ENVIRON | os.environ | An array contining the vlaues of the environment variabales. | 
| FILENAME | FILENAME | The name of the current input file. If no file is specified the value of FILENAME is '-' | 
| FNR | FNR | The ordinal number of the current record in the current file. | 
| FS | FS | The field separator. default value = ' '(space) | 
| NF | NF | The number of fields in the current input record. | 
| IGNORECASE | Not implemented | Case sensitivity flag for regular expressions. |
| NR | Not implemented | The number of input records seen so far (Not set to zero on new file). | 
| OFMT | Not necessary | The default output format for numbers. |
| OFS | Not necessary | The output field spparator. | 
| ORS | Not necessary | The output record separator. |
| RS | Not implemented | The input record separator (default = '\n'). | 
| RSTART | Not implemented | Index of the first charachter matched by match, 0 if no match. | 
| RLENGTH | Not implemented | Length of the string matched by match; -1 if no match. | 
| SUBSEP | Not implemented | The string used to separate multiple subscripts in array elements. | 

### Arrays
Normal python array handling.

### Data types
Python data types&nbsp;

### Comments
Normal python comments can be used. Both # and """ will work.

### patterns
The pattern used for selection has the form: /re regular expression/,
see the python re module for more information.

### I/O Statements

| AWK | PYAWK | Explanation |
| :------------------ | :----- | :----------- |
| getline | Not implemented | Set the internal field variables, NF, NR and FNR from the next input line. | 
| getline&nbsp;<&nbsp;filename | getline(filename) | Set the internal field variables, NF, NR and FNR from the next input line of the given file. |
| getline var | getline(var) | Set the internal field variables, NF, NR and FNR from the string variable. |
| getline&nbsp;var&nbsp;<&nbsp;file | Use Python file handling | Set var from the next record og the given file. |
| next | next() | Stop processing the current input record. The next input record is read and processing starts over with the first pattern in the pyawk program. If the end of the input data is reached, the END rule is executed. |
| getline&nbsp;var&nbsp;<&nbsp;file | Use Python file handling | Set var from the next record og the given file. |
| print | Use Python print statement. | |
| printf() | Use Python print statement. | |

### Special file names
  ```
  '/dev/stdin' Use sys.stdin
  '/dev/stdout' Use sys.stout
  '/dev/stderr' Use sys.stderr
  '/dev/fd/n' Use normal python file handling
  ``` 

### String Functions
All of the awk string functions have equivalents in the python string module or string type methods.

### Extensions
The following are syntax extensions that do not appear in awk:

### INSTALLATION
At present only the pyawk.py file exists (no installer) so just copy pyawk.py somewhere where the python interpreter will find it, eg /usr/local/lib/python3.?/site-packages.

Roger Wenham 28/8/2018
