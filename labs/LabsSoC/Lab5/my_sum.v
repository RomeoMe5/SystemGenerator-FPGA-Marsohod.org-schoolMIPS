module my_sum (Ain, Bin, Ci, Sout, Co);
  input Ain, Bin, Ci;
  output Sout, Co;
  
  wire [3:0] Ain, Bin, Sout, C;
  wire Ci, Co;

bitsum sum1(Ain[0], Bin[0], Sout[0], Ci, C[0]);
bitsum sum2(Ain[1], Bin[1], Sout[1], C[0], C[1]);    
bitsum sum3(Ain[2], Bin[2], Sout[2], C[1], C[2]);
bitsum sum4(Ain[3], Bin[3], Sout[3], C[2], C[3]);

assign Co = C[3];

endmodule
 
module bitsum (A, B, S, Cin, Cout);
  input A, B, Cin;
  output S, Cout;
  
  wire A, B, S, Res;
  wire c1, c2, Cin, Cout;
    
  xor(Res, A, B);
  and(c1, A, B);
  xor(S, Cin, Res);
  and(c2, Cin, Res);
  or(Cout, c1, c2);
  

endmodule

