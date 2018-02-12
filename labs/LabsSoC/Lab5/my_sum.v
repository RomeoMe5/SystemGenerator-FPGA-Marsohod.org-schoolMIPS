module my_sum (a, b, s);
  input a, b;
  output s;
  
  wire [3:0] a, b, s, c_wire;
  wire c;

  bitsum sum1(a[0], b[0], s[0], c, c_wire[0]);
  bitsum sum2(a[1], b[1], s[1], c_wire[0], c_wire[1]);    
  bitsum sum3(a[2], b[2], s[2], c_wire[1], c_wire[2]);
  bitsum sum4(a[3], b[3], s[3], c_wire[2], c_wire[3]);

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
