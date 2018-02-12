module mult_acc (out, ina, inb, clk, clr);

input [7:0] ina, inb;
input clk, clr;
output [15:0] out;

wire [15:0] mult_out, adder_out;
reg [15:0] out;

parameter set = 0;
parameter hld = 0;

function [15:0] mult;
     input [7:0] a, b ;
     integer i ; 
  begin
     mult = 0;
     for (i =0; i <=7; i = i + 1) 
	if (a[i] == 1) 
	   mult = mult + (b << i) ; 
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
	$setup (inb, posedge clk, set);
	$hold (posedge clk, inb, hld);
	$hold (posedge clk, ina, hld);
endspecify
		
endmodule
