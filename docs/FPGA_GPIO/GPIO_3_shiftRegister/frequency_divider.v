module frequency_divider(
	input_clk,
	output_clk
);
	input input_clk;
	output reg output_clk;
	
	reg[29:0] divider;
	
	initial
	begin
		divider = 20'b0;
	end
	
	always @(posedge input_clk)
	begin
		divider = divider + 1'b1;
		output_clk = divider[20];
	end

endmodule
