module Lab7_prot(AB_led, iAB_led, clk);
  reg[15:0] A_in, B_in, iA_in, iB_in;
  input clk;
  output[3:0] AB_led, iAB_led;
  reg complx_control;
  reg[1:0] math_control;
  wire[15:0] AB_out, iAB_out, A_out, B_out, iA_out, iB_out;
  wire[15:0] add_AB_out, add_iAB_out;
  wire[15:0] sub_AB_out, sub_iAB_out;
  wire[15:0] mul_AB_out, mul_iAB_out;
  wire[15:0] div_AB_out, div_iAB_out;
  reg [25:0] counter;
  reg [1:0] inner_clk_cnt;

  Multiplication mult(A_out, B_out, iA_out, iB_out, complx_control, clk, mul_AB_out, mul_iAB_out);
  Division div(A_out, B_out, iA_out, iB_out, complx_control, clk, div_AB_out, div_iAB_out);
  Addition add(A_out, B_out, iA_out, iB_out, clk, add_AB_out, add_iAB_out);
  Substract sub(A_out, B_out, iA_out, iB_out, clk, sub_AB_out, sub_iAB_out);
  mux_complx mx_cmplx(A_in, B_in, iA_in, iB_in, complx_control, A_out, B_out, iA_out, iB_out);
  mux_math mx_mth(add_AB_out, add_iAB_out, sub_AB_out, sub_iAB_out, mul_AB_out, mul_iAB_out, div_AB_out, div_iAB_out, math_control, AB_out, iAB_out, clk);

  assign AB_led = AB_out[3:0];
  assign iAB_led = iAB_out[3:0];

  initial
  begin
    complx_control = 0;
    math_control = 2'b00;
    A_in = 10'd5;
    B_in = 10'd4;
    iA_in = 10'd3;
    iB_in = 10'd1;
    counter = 26'b0;
    inner_clk_cnt = 2'b0;
  end

  always@(posedge clk)
	 begin
    if(counter == 26'd5)
      begin
        counter = 26'b0;
        inner_clk_cnt = inner_clk_cnt + 1'b1;
      end
    else
    counter = counter + 1'b1;

    if (inner_clk_cnt == 2'b11)
      begin
        if (math_control == 2'b11)
          begin
            if (complx_control == 1'b1)
              begin
                math_control = 2'b00;
                inner_clk_cnt = 2'b00;
                complx_control = 1'b0;
              end
            else
              begin
                math_control = 2'b00;
                inner_clk_cnt = 2'b00;
                complx_control = complx_control + 1'b1;
              end
          end
        else
        begin
          inner_clk_cnt = 2'b00;
          math_control = math_control + 1'b1;
        end
      end
   end

endmodule
