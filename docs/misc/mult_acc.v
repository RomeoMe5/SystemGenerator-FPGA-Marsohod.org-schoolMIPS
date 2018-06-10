`timescale 1 ns/ 10 ps

module mult_acc (out, ina, inb, clk, clr);

input [7:0] ina, inb;
input clk, clr;
output [15:0] out;

wire [15:0] mult_out, adder_out;
reg [15:0] out;

parameter set = 10;
parameter hld = 20;

function [15:0] mult;
     input [7:0] a, b ;
     reg [15:0] r;
     integer i ; 
  begin
     if (a[0] == 1)
          r = b;
     else
          r = 0 ;
      for (i =1; i <=7; i = i + 1)
         begin
            if (a[i] == 1)
                r = r +b <<i ; 
            end
  mult = r;
  end
endfunction    


assign adder_out = mult_out + out;

always @ (posedge clk or posedge clr)
   begin 
	if (clr) 
		out <= 16'h0000;
	else 
		out <= adder_out;
   end 

// Function Invocation
assign   mult_out = mult (ina, inb);

specify 
	$setup (ina, posedge clk, set);
	$hold (posedge clk, ina, hld);
	$setup (inb, posedge clk, set);
	$hold (posedge clk, inb, hld);
endspecify
		
endmodule
