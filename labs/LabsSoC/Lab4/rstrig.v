
`timescale 1 ns/ 10 ps

module rstrig (Clk, R, S, Q);
  input Clk, R, S;
  output Q;
  
  wire R_g, S_g, Qa, Qb;
  reg Clk_r, R_r, S_r;
  parameter period = 50;
  
  initial
    begin
      Clk_r = 1'b0;
      forever #(period /2) Clk_r = ~Clk_r;
    end
  initial
    begin
      R_r = 1'b0;
      #40 R_r = 1'b1;
      #80 R_r = 1'b0;
      #130 R_r = 1'b1;
    end
  initial
      begin
      S_r = 1'b0;
      #80 S_r = 1'b1;
    end
    initial
    #180 $finish;
    
  and(R_g, R, Clk);
  and(S_g, S, Clk);
  nor(Qa, R_g, Qb);
  nor(Qb, S_g, Qa);
  
  assign Q = Qa;
  assign Clk = Clk_r;
  assign R = R_r;
  assign S = S_r;
  
endmodule

