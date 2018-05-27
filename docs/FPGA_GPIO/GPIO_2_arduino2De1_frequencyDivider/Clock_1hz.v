module Clock_1hz(
	input_clk,
	output_clk
);
	input input_clk;
	output reg output_clk;
	
	reg signal;
	reg[24:0] counter;
	reg[24:0] const_data = 25'b1011111010111100001000000;
	
	initial
	begin
		signal = 1'b0;
		counter = 25'b0;
	end

	always@(posedge input_clk)
	begin
		counter = counter + 1'b1;
		if(counter == const_data)
		begin
			signal = ~signal;
			counter = 25'b0;
		end
			output_clk = signal;
	end

endmodule
