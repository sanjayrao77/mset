# mset.py, a tool to generate text documents from snippets

## Overview

This can be used to assemble a book or large document from small components. Instead of having a flat
file, there are many record entries and a final text output is generated from the records.

By breaking text into small components, maintenance can be easier than with traditional word processors.

For example, rather than editing existing sentences, you can instead append new sentences to replace older
ones in the generated output. To revert such changes, you can disable the new sentence, again
without modifying the sentences.

This also allows you to have multiple output versions from the same source file. For examples, I
interleave an outline with my text copy and then the program can make a clean "release" version or a "debug"
version with the outline interleaved in the output.

I can also use a single source file to create both HTML/XHTML and UTF8 output.

*mset* is a successor to [bookbits](https://github.com/sanjayrao77/bookbits).

*mset* can also be used as a simple database, generating spreadsheets or reports as output.

## Installing

All you need is mset.py. You can download it to a standard system with python3 installed.
Unix systems will require a "chmod +x" to make it executable.

For the sake of security, you can scan the code to see that there isn't anything malicious. It's
currently less than 1500 lines.

## Usage

Assuming you have a text file, you can run "mset.py file.txt" to print the ".mainmenu" node or
"bookbits.py file.txt .NAME1 .NAME2 ..." to print the nodes of NAME1, NAME2, etc.

## Quick start

To get a quick look, you can download helloworld.txt and story.txt as example files.

With that done, you can run "mset.py helloworld.txt" to see the main menu in helloworld.txt

After you see the menu text, you can run "mset.py helloworld.txt .hello".

For the story example, you can run "mset.py story.txt" to see the main menu and then try the options printed.
For example, "mset.py story.txt .outline" will print the plot outline.

## Command line arguments

Command line arguments can be used to print different output.

You can specify one or more Nodes, starting with a period. For example, "mset.py story.txt .chapter1 .chapter2 .debug".

Global variables can be set from the command line with a "+" prefix, with "+xxx=yyy", where xxx is the variable name
and yyy is the value. Without an equals sign, it will set the value to numerical "1" or True. With an empty yyy, it
sets to numerical "0" or False. With a non-empty yyy, it sets it to the string "yyy".
For example, "mset.py examples/taxes.fancy.txt .report +html" will set "html" to True while "+html=" would have set it to False.

Global variables can be used with many commands, see below.

You can also disable one or more Nodes, starting with a period and hyphen. For example, "mset.py story.txt .chapters .-debug".
This will print all the chapters without any Nodes marked with ".debug".

You can also specify the following:
    1. --html: to generate html output from escape sequences
    2. --xhtml: to generate xhtml output from escape sequences
    3. --text: to generate ascii output from escape sequences
    4. --force: to disable assert checking
    5. --p0dump: to debug first phase of parsing
    6. --gvdump: to debug global variables
    7. --nodesdump: to debug node parsing
    8. --namesdump: to debug names of nodes
    8. --debug: to print more information on errors

You can also specify multiple filenames. They should all end in ".txt" so they are recognized as filenames.

## Nodes

A basic structure in input files is a "Node" which looks like a paragraph. A blank line will separate one Node from
another. You can also enter Nodes one-per-line, detailed below in the "single lines" section.

Within a Node, you can enter text as words separated by spaces, just like english. Avoid starting words with '.' or
'\\' for now. Words starting with '.' are interpreted as instructions and words starting with '\\' are used for
escape sequences. To start an output word with a '.', you can prepend '\\', e.g. "\\.hello" will print ".hello" in
the output text. To start an output word with a '\\', you can prepend another one, e.g. "\\\\boo" will print "\\boo"
in the output text.

Most commands can be included in a Node in any position with no change of meaning. You can include a Node in another
Node by writing a word starting with a period (or using the .\_join command). For example including ".debug" will add
the Node to the Node named "debug". You can have this ".debug" at the beginning of the Node, the middle or the end with
no change in effect.

Example Node:
```
.=story

.story Hi world

I .story was wondering

what goes
.story

.story
on

in the world .story
```

Running this creates:
```
$ ./mset.py examples/example-1.txt .story
Hi world I was wondering what goes on in the world
```

## Defining a Node

Every Node has to be defined before use. It must be included in the input file before it is used.

To define a Node, you can use the ".=xxx" or ".\_name(xxx)" commands.

E.g., these lines define a Node called "mainmenu" and gives it some text. All the examples below are
equivalent:
```
.=mainmenu This is the main menu

._name(mainmenu) This is the main menu

This is the main menu .=mainmenu

This is ._name(mainmenu) the main menu
```


## Escapes

Not all escapes are interpreted. If you have a normal word with a backslash in the middle,
that backslash does *not* need to be escaped.

If you start a word with a backslash, it will be checked as an escape sequence. E.g.: "\n" or "\tab" by themselves
will print a newline or tab. You can also group escapes together, for convenience. E.g.: "\n\tab" will print a newline
and a tab.

The following escape sequences can be used within a Node:
1. "\\\\word" this lets you start a word with a slash, it creates "\\word" in output and ignores trailing escape sequences
2. "\\n" this adds a newline in output
3. "\\s" and "\\space" this creates a forced space. Normally, excess spaces are removed but this can be used to add some.
4. "\\t" and "\\tab" this adds a tab in output
5. "\\bs" and "\\backspace" this removes a preceding space, if there is one
6. "\\B" and "\\Bold" this indicates the start of bold text
7. "\\b" and "\\bold" this indicates the end of bold text
8. "\\I" and "\\Italic" this indicates the start of italic text
9. "\\i" and "\\italic" this indicates the end of italic text
10. "\\P" and "\\Paragraph" this indicates the start of a paragraph
11. "\\p" and "\\paragraph" this indicates the end of a paragraph
12. "\\U" and "\\Underline" this indicates the start of underlined text
13. "\\u" and "\\underline" this indicates the end of underlined text
14. "\\br" this indicates a line break, creating \<br\> for html output

Example:
```
.=mainmenu \P \Bold Hi world!! \bold This \n is \n an \n example of \n\n escaping.
```

Output:
```
$ ./mset.py examples/example-2.txt
<p><b>Hi world!!</b> This
is
an
example of

escaping.
$ ./mset.py examples/example-2.txt --text
*Hi*world!!* This
is
an
example of

escaping.
```

## Escapes in commands

If you want to escape characters within a command, you can enclose the parameter with parentheses. For example,
.\_map(.price,(10.31)).

## Node grouping

Nodes can have relationships with other Nodes. A Node can be a *component*, *example* or *item* of another Node. They can
also be mapped to each other with functions.

A Node must first be defined and exist earlier in the input file before another Node can relate to it.

Often, a Node will be used as a container for other Nodes. This first node is a normal Node and the text may be used to
describe the container. The other Nodes will either be *components*, *examples* or *items* of the container.

A *component* is a portion of a body. The container is meant to mean the body and is the union of its components. So,
if you container is "Chapter1", the components could be the paragraphs and sentences which compose Chapter 1.

An *example* is another body which portrays the first body. For example, "Camry" is an *example* of "Car". This is different
from a *component* relation.

An *item* is a member of a collection with the name of the container. For example, the container could be "2023 taxes" and the
item could be "IRS receipt". These two things don't have a strong relationship but the "IRS receipt" is categorized under
"2023 taxes" for organizational convenience.

To add a Node as a component to a container Node, you can include ".\_join(.xxx)" in the Node, where xxx is the name of the container.
As a shorthand, you can include ".xxx". To add a Node as an *example*, you can use ".\_join.(xxx.\_example)" or ".xxx.\_example",
where xxx is the name of the container. To add an *item*, you can use ".\_join(.xxx.\_item)" or ".xxx.\_item". You could also
use ".xxx.\_component" instead of ".xxx".

As a shorthand, you can use \_c instead of \_component, \_e instead of \_example and \_i instead of \_item. E.g.: ".xxx.\_i".

## .mainmenu

The default Node to print is "mainmenu", if no command line options are given. There's nothing else special about it. But, it's
a good place to give help to the user. You can get this help by running "mset.py file.txt" without any Nodes specified.

As with all Nodes, if .mainmenu has no components, then the defining Node will be printed. If there *are* components, then
the defining Node will *not* be printed and only the *component* type members will be printed.

You can print *example* and *item* members instead with the \_examples and \_items suffixes.
E.g.: "mset.py file.txt .mainmenu.\_items".
The following are equivalent: \_example, \_e, \_examples. The following are equivalent: \_item, \_i, \_items.

If you want to print a Node itself and not its members, you can use the \_self suffix. E.g.: "mset.py file.txt .mainmenu.\_self".
You can use \_s as a shorthand for \_self.

## Default group

If a Node belongs to no Node at all and it doesn't define itself, it is automatically added to a Node with the name "\_default".
You can print this on the command line by adding ".\_default" or "." as a parameter. E.g.: "mset.py file.txt .".

To explicitly add a Node to this group, you can add ".\_default" or ".\_join(.\_default))" to a Node.

This can be useful if you have a normal text file and don't want to modify every paragraph to join a Node.

## Asserts and --force

If you'd like to check output self-consistency, you can use .\_set(x) .\_unset(x) and .\_assert(x) commands.
The "x" in these examples are names of boolean variables, in their own namespace.

You can disable assert checks for a run by using the "--force" argument.

.\_set(x) will set x=True. .\_unset(x) will set x=False. .\_assert(x,y,z) will create
an error if x, y or z are not currently True. You can use "-x" to create an error if x is not currently False (E.g.: .\_assert(-x,y,z)).

These commands are run sequentially with the output, rather than the order in the text file. By running with the output,
later output can check if specified output has been created earlier.

Example, suppose you want to check that XYZ has been introduced before referencing it later in a story:
```
. .=story story body
. .=chapter1 Chapter 1
. .=chapter2 Chapter 2
. .=chapter3 Chapter 3

.story .chapter1 Definition: an XYZ is a potato. ._set(XYZ_isexplained) \n

.story .chapter2 The sky is blue. \n

.story .chapter3 Our hero saw an XYZ on the ground. ._assert(XYZ_isexplained) \n
```

If you run "mset.py examples/example-3.txt .story" you get the following. Everything is fine.
```
Definition: an XYZ is a potato.
The sky is blue.
Our hero saw an XYZ on the ground.
```

If you run "mset.py examples/example-3.txt .chapter3" you get an error:
```
Exception: Error: Error: Runtime variable assert failed: "XYZ_isexplained" not found
```

You can use "--force" to ignore the warning. E.g.: "mset.py example.txt .chapter3 --force" prints chapter 3.

## Output vars, set, setstring, unset, sum and printvar

The *set* command was already mentioned with the *assert* command. It can also be used to set running variables.

These commands are used on the output, in the order of the output. This is most useful for adding numbers to
give running totals.

You can use ".\_set(a,b)" to set variable "a" with the numerical value of "b". (You can also use set(a,b,c)
to set the fraction (b/c)). E.g.: ".\_set(potatoes,10.5)" or ".\_set(potatoes,21,2)"

You can add to an existing variable with the ".\_sum(a,b)" command. E.g.: ".\_sum(potatoes,3,2)" to get 12
potatoes.

Example:
```
.=foo

.foo ._set(potatoes,0) I took an empty bag,

.foo ._sum(potatoes,21,2) added 21 half-potatoes,

.foo ._sum(potatoes,3,2) added 3 more half-potatoes,

.foo and in the end I had \space ._printvar(potatoes) \space potatoes.
```

```
$ mset.py examples/example-4.txt .foo
I took an empty bag, added 21 half-potatoes, added 3 more half-potatoes, and in the end I had 12 potatoes.
```

## Conditional inclusion

Conditional inclusion can remove Nodes before they are included. They can be excluded based on global variables
in the input file or from the command line.

This is different from Suppression in that suppressed Nodes are loaded and then disabled while conditionally excluded
Nodes are never loaded.

Because conditionally excluded Nodes are not loaded, you can have multiple Nodes with the same name as long as only
one is included at a time.

To set a global variable, you can use ".\_globalint(xxx)" in the input file or "+xxx" on the command line, where xxx
is the name of the variable.

You can conditionally exclude a node by adding ".?-xxx" to a Node. Doing this will exclude the Node
if xxx is set.

To do the reverse, you can use ".?xxx", ".?+xxx". Doing this will exclude the Node if xxx is *not* set.

All named Nodes will automatically exclude themselves if their name has been set to 0 with a command like ".\_global0(xxx)".
This is equivalent to ".\_globalint(xxx,0)".

Example:
```
.=chapter1 Chapter 1

.=u1_1 .chapter1 It was the best of times, it was the blurst of times.

.=u1_2 .chapter1 It was the best of times, it was the worst of times. ._global0(u1_1)
```

```
$ mset.py examples/example-5.txt .chapter1
It was the best of times, it was the worst of times.
```

## Suppression

Nodes can be suppressed from output by suppressing the Nodes or a container the Nodes belong to. Nodes that are suppressed
will not be printed in output.

This can be useful if you have multiple Node types interleaved amongst containers and you only want to print some of them.
For example, you might have internal editing comments that you want excluded in a final output.

You can specify a Node to suppress by including either ".-xxx" or ".\_suppress(.xxx)" in a Node, where xxx is the name
of the Node to suppress. If you want to suppress the components of xxx, you can use "xxx.\_components" or "xxx.\_c"
instead of xxx. You can also use "xxx.\_all" or "xxx.\_a" to mean all members and xxx itself.

You can also suppress Nodes from the command line with ".-xxx" as a command line argument.

You can invert a suppression with ".+xxx" or ".\_unsuppress(.xxx)", which makes a previously suppressed Node active again.

Example:
```
. .=chapter1 Chapter 1
. .=debug Internal comments

.chapter1 It was the best of times,

.chapter1 .debug \n DEBUG: Think of something clever! \n

.chapter1 it was the worst of times.
```

```
$ mset.py examples/example-6.txt .chapter1
It was the best of times,
DEBUG: Think of something clever!
it was the worst of times.
$ mset.py examples/example-6.txt .chapter1 .-debug
It was the best of times, it was the worst of times.
```

## Supersets

You can create a Node that includes members from other Nodes. This allows you to create supersets.
The members will be interleaved to maintain their order in the input file. You can do this with by adding
".\_adopt(.xxx)" to the superset, where xxx is the source Node name.

This allows you to create collections of other nodes, as an alternative to Suppression.

By default, a superset will copy all members (components, examples, items) from the source. To select
only one type, you can use the \_components, \_examples or \_items suffixes. E.g.: ".\_adopt(.xxx.\_components)".

## Inline text aka include

You can include the text from another Node with the ".\_include(.xxx)" command or ".\<xxx" shorthand, where xxx
is the name of the node.

This inclusion will be subject to Suppression, where suppressed Nodes will not be included.

Example:
```
.=foo Make it shorter

.=bar The whole city saw the billboard. It proclaimed " .<foo " and people understood.
```

Running "mset.py examples/example-7.txt .bar" creates:
```
The whole city saw the billboard. It proclaimed " Make it shorter " and people understood.
```

In the last example, it adds spaces around the inlined text. To remove those spaces, you can add \\bs or \\backspace
escapes like so:

Running "mset.py examples/example-8.txt .bar" creates:
```
.=foo Make it shorter

.=bar The whole city saw the billboard. It proclaimed " \bs .<foo \bs " and people understood.
```

## Single lines

Nodes are usually separated from each other with blank lines. If you'd like to have Nodes next to each other
without blank lines, you can do that by starting a line with ". ", that is a period and a space. Any line
with that beginning will be considered a self-contained Node definition.

If you actually want to start a Node with a period and a space, you can add a space before it to remove this
detection. Starting with any command will also disable this detection.

This is useful for defining many small Nodes or adding lots of short comments.

Example:
```
. .=chapter1 Chapter 1
. .=chapter2 Chapter 2
. .=chapter3 Chapter 3
```

This example creates 3 Nodes even though there aren't blank lines.

## Internal comments (not included in output)

Often it's useful to include a note in the input that you don't want included in output. These are often
called comments.

You can use the ".#" command to ignore any text following it. A line starting with ".#" will be completely
ignored. A line with ".#" in the middle will have any trailing text ignored.

## Global vars

It's possible to set variables that can be accessed anywhere in the file.

This can be useful if you want to
change the overall behavior. For example, in examples/taxes.fancy.txt, "html" is used as a variable to control whether
to make html output.

This can also be used to add multiple numbers together to do sums.

You can set variables on the command line with "+" (see *Command line arguments* above) or within the
file with the .\_global0, .\_globalint and .\_globalstring commands. You can print variables with the
.\_printvar command. You can use the .\_sum command to add to variables.

## Generated Nodes

It's possible to define Nodes that are generated from parameters. This is similar to macro functions in the
C Preprocessor.

You can access the generating parameters like global variables, with the ".$xxx" and ".\_variable(xxx)" commands.
These generating parameters can only be accessed within the generator Node.

Example:
```
.=foo(a,b,c) .$a is the way to .$b to .$c

.=bar .<foo(hi,there,world) \n .<foo(how,are,things)
```

```
$ mset.py examples/example-9.txt .bar
hi is the way to there to world
how is the way to are to things
```

## Literals: .\_literal and .\_l

Sometimes it's convenient to create a node with a short, simple string. Rather than defining them explicitly,
you can use the built-in .\_literal(a) and .\_l(a) generating Nodes.

This is useful if you want to map a Node to a short value without having to define the value. See *Maps aka functions* below.

Example:
```
.=foo This is the time of day .<_l(what)

$ mset.py exaples/example-10.txt .foo
This is the time of day what
```

## Maps aka functions

It's possible to map a Node to another Node, by way of a third Node. This is useful for organizing data. For example,
you could map .potato to .onedollar by way of a .price node. You could later retrieve the result of the map to find the
price of the potato.

You can do this with ".xxx=.yyy" or ".\_map(.xxx,.yyy)" where xxx is the function Node and yyy is the target node.

As a shorthand, you can use ".xxx=zzz", which will map to .\_literal(zzz).

Example:
```
.=price Price

.=potato ._map(.price,(1.00)) Potatoes are round.

.=2bucks 2 dollars

.=carrot ._map(.price,.2bucks) Carrots are not potatoes.

.=foo Price of a potato: ._unmap(.potato,.price) \bs . \n
Price of a carrot: ._unmap(.carrot,.price) \bs .
```

This creates:
```
$ mset.py examples/example-11.txt .foo
Price of a potato: 1.00.
Price of a carrot: 2 dollars.
```

## Named members

If you have a complicated dataset, you may want to organize the Nodes into sub-Nodes in a hierarchy. In this way,
you can access the sub-Nodes as members of the parents.

You can access members with the period character. The default member is components, but you can modify this with
\_example and \_item words. E.g.: "foo.\_example.bar" or "foo.\_e.bar" will access the "bar" example Node in the "foo"
container Node.

For example, if you want to organize all your functions together:
```
.=functions Functions

.=functions.price Price

.=potato ._map(.functions.price,(1.00)) Potatoes are round.

.=2bucks 2 dollars

.=carrot ._map(.functions.price,.2bucks) Carrots are not potatoes.

.=foo Price of a potato: ._unmap(.potato,.functions.price) \bs . \n
Price of a carrot: ._unmap(.carrot,.functions.price) \bs .
```

```
$ mset.py examples/example-12.txt .foo
Price of a potato: 1.00.
Price of a carrot: 2 dollars.
```

## All special words and commands

### \_default

There is a reserved Node called "\_default". Input paragraphs without any Node membership,
names or other commands will be aded to this Node as a component.

This lets you add plain text files without having to mark up every paragraph. Those paragraphs
will be printed with a ".<\_default" command.

### \_literal(a) and \_l(a)

There is a reserved generating node called "\_literal" and "\_l". It's simply: ".\_literal(a) .$a". This
lets you create Nodes implicitly if they are very simple.

This is useful with mapping, if you want to map to a simple value. For example, ".price=\_l(2.00)" will map
to a Node of "2.00" with the ".price" Node function.

This creates an actual Node of name "\_l(2.00)" and reuses it if it is accessed multiple times.

You can refer to the Node with "\_literal" or "\_l" but the generated names won't match if you use both.
That is, "\_literal(2.00)" doesn't match "\_l(2.00)".

### $a

You can access a variable with the dollar sign. For example, ".\_globalstr(bar,price) .functions.$bar"
will add the Node to ".functions.price".

There are many contexts where variable substitution works. This applies to global variables (\_global0, \_globalint, \_globalstring)
as well as output variables (\_set,\_setstring,\_unset,\_sum,\_printvar,\_assert).

### .?a or .?+a or .?-a

Nodes can be conditionally excluded based on global variables. Variables can be set with the \_global0, \_globalint and \_globalstring
commands.

A Node can be excluded by including a ".?xxx" command inside it. If "xxx" is undefined or has value 0, then such a Node will not
be loaded. The ".?a" and ".?+a" commands are the same. You can use a ".?-xxx" command to flip the exclusion. A Node including that
command will be excluded if xxx *is* defined and has value *non-0*.

A quick way do define 0 is using the \_global0 command. E.g.: ".\_global0(debug)" will set the global variable "debug" to 0.

See the *Conditional inclusion* section for more examples.

### \_join(a) or .a

When placed in a Node, this adds the Node to the Node named "a". You can use \_components, \_component, \_c, \_examples, \_example, \e,
\_items, \_item, \_i suffixes to control which container to add it to. By default, it is added as a component.

### \_include(a) or \_include(a,b) or .\<a

A Node can include other Nodes for the purpose of printing their contents. You can include either a Node itself, its components,
examples or items. You can also add text between members by using the \_include(a,b) form, where *b* is either text or a Node
to be printed between members.

### \_map(a,b) or .a=b

You can map to another Node via a third Node with the \_map command. See the *Maps aka functions* section for more information.

### \_unmap(a,b)

You can retrieve a previous mapping to another Node with the \_unmap
command. See the *Maps aka functions* section for more information.

### \_name(a) or .=a

This registers the given Node with the name "a". Names can be within another Node or toplevel.

To register a name within another Node, use the period character. E.g.: ".=parent.child" will register the name "child"
with the toplevel parent Node "parent".

See the *Named members* section for more information.

### \_suppress(a) or .-a

When printing a Node, you can suppress the printing of select child Nodes based on their membership to other Nodes.

See the *Suppression* section for more information.

### \_unsuppress(a) or .+a

When printing a Node, you can suppress the printing of select child Nodes based on their membership to other Nodes.
You can also reverse suppressions with the \_unsuppress command.

See the *Suppression* section for more information.

### \_set(a) or \_set(a,b) or \_set(a,b,c)

These are used to set an numerical output variable. Output variables are set and used in order of the output. This
allows sequence checking and adding numbers.

You can set an integer to 1 with \_set(a).

You can set an arbitrary number with \_set(a,b), where "a" is the variable and "b" is a decimal representation.

You can set a rational fraction with \_set(a,b,c) where "a" is the variable and "b" and "c" are integers.

See the *Output vars* and *Asserts* sections for more information.

### \_setstring(a,b)

This allows you to set a string as an output variable. Output variables are set and used in the order of the output,
which is different that global variables.

If you want to change the value of a variable along with the output, you can use this.

See the *Output vars* section for more information.

### \_unset(a)

This is shorthand for setting an output variable to 0. This is useful with \_assert. An assert will fail if the
variable has been \_unset.

See the *Output vars* and *Asserts* sections for more information.

### \_sum(a) or \_sum(a,b)

If you want to do a running sum in the order of the output, you can use output variables and the \_sum commands.

Used with one parameter, it will add the value of "a" to the "sum" variable, which starts at 0.

Used with two parameters, it will add the value of "b" to the "a" variable.

See the *Output vars* section for more information.

### \_printvar(a)

You can use \_printvar(a) to print the "a" variable. If "a" exists as an output variable, it will print that. Otherwise,
it will check the global variables and print "a" if it exists as a global variable.

See the *Output vars*  and *Global vars* sections for more information.

### \_assert(a)

If you want to check for internal consistency in the output, you can use the \_set, \_unset and \_assert commands to
set flags and check for them.

See the *Assert* section for more information.

### \_global0(a)

This sets the global variable "a" to integer 0.

See the *Global vars* section for more information.

### \_globalint(a) or \_globalint(a,b) or \_globalint(a,b,c)

These set global variables to numerical values.

See the *Global vars* section for more information.

### \_globalstring(a,b)

These set global variables to string values.

See the *Global vars* section for more information.

### \_adopt(a)

You can combine multiple Nodes with the \_adopt(a) command, where "a" is the path to a Node.

The combination will be sorted in the order of the input. For example, you could include story and outline text
together and the combination could interleave the two based on their interleaving in the input file.

See the *Supersets* section for more information.
