module check_keys(
	clk,
	input_sw_wire,
	check_result,
	output_res,
	output_final_res
);

	input clk;
	input[9:0] input_sw_wire;
	input check_result;
	output reg output_res;
	output reg output_final_res;
	
	initial
	begin
		output_res = 1'b0;
		output_final_res = 1'b0;
	end
	
	always@(posedge clk)
	begin
		if(!check_result)
		begin
			output_final_res = 1'b0;
			case(input_sw_wire)
				10'b1111111111 : output_res = 1'b1;	
				10'b0011110100 : output_res = 1'b1;
				10'b1001011110 : output_res = 1'b1;
				10'b0011110010 : output_res = 1'b1;
				10'b1001001010 : output_res = 1'b1;
				10'b1010110101 : output_res = 1'b1;
				10'b1111110101 : output_res = 1'b1;
				10'b0001011110 : output_res = 1'b1;
				10'b1010101010 : output_res = 1'b1;
				10'b1111100000 : output_res = 1'b1;
				10'b0001001111 : output_res = 1'b1;
				10'b1010011100 : output_res = 1'b1;
				10'b0101111100 : output_res = 1'b1;
				10'b1000110001 : output_res = 1'b1;
				10'b1011110100 : output_res = 1'b1;
				10'b1000110101 : output_res = 1'b1;
				10'b0001010101 : output_res = 1'b1;
				10'b1010011010 : output_res = 1'b1;
				10'b0101101010 : output_res = 1'b1;
				10'b1010010101 : output_res = 1'b1;
				10'b1100101010 : output_res = 1'b1;
				default : output_res = 1'b0;
			endcase
		end
		else begin
			output_res = 1'b0;
			if(input_sw_wire == 10'b1101001100)
			begin
				output_final_res = 1'b1;
			end
			else begin
				output_final_res = 1'b0;
			end
		end
		
	end

endmodule
