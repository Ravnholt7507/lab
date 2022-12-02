main :-
   open('Answer.txt', write, File),   
   forall(query(Q), (Q -> writeln(File,yes) ; writeln(File,no))),
   writeln(File, '************************'),
   close(File).

:- initialization(main).
