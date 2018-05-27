module ref_sum (Ain, Bin, Ci, Sout, Co);
  input Ain, Bin, Ci;
  output Sout, Co;
  
  wire [3:0] Sout, Ain, Bin;
  reg [4:0] S;

  
  always @(Ain, Bin, Ci)
  S = Ain + Bin + Ci;
  
  assign Sout = S[3:0];
  assign Co = S[4];
  
endmodule
