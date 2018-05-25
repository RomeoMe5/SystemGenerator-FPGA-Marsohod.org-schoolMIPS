module mux_complx(A_in, B_in, iA_in, iB_in, complx_control, A_out, B_out, iA_out, iB_out);
  input[15:0] A_in, B_in, iA_in, iB_in; 
  input complx_control;
  output[15:0] A_out, B_out, iA_out, iB_out;
  reg[15:0] A_out, B_out, iA_out, iB_out;

  always @(A_in, B_in, iA_in, iB_in, complx_control)
    case (complx_control)
      0: 
			begin 
				A_out = A_in;
				B_out = B_in;
				iA_out = A_in;
				iB_out = B_in;
			end
      1:
			begin
				A_out = A_in;
				B_out = B_in;
				iA_out = iA_in;
				iB_out = iB_in;
			end
      default: 			
			begin 
				A_out = A_in;
				B_out = B_in;
				iA_out = A_in;
				iB_out = B_in;
			end
    endcase

endmodule
