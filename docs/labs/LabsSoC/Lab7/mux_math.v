module mux_math(add_AB, add_iAB, sub_AB, sub_iAB, mul_AB, mul_iAB, div_AB, div_iAB, mux_control, AB_out, iAB_out, clk);
	input[1:0] mux_control;
	input clk;
	input[15:0] add_AB, add_iAB, sub_AB, sub_iAB, mul_AB, mul_iAB, div_AB, div_iAB;
	output[15:0] AB_out, iAB_out;
	reg[15:0] AB_out, iAB_out;

	always@(posedge clk)
		case(mux_control)
			0:
				begin
					AB_out = add_AB;
					iAB_out = add_iAB;
				end
			1:
				begin
					AB_out = sub_AB;
					iAB_out = sub_iAB;
				end
			2:
				begin
					AB_out = mul_AB;
					iAB_out = mul_iAB;
				end
			3:
				begin
					AB_out = div_AB;
					iAB_out = div_iAB;
				end
		endcase
endmodule
