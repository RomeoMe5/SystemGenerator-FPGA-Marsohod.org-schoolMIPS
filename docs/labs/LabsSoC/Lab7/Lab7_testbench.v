module Lab7_testbench;
  reg[15:0] A_in, B_in, iA_in, iB_in;
  wire clk;
  reg clk_reg, complx_control;
  reg[1:0] math_control;
  wire[15:0] AB_out, iAB_out, A_out, B_out, iA_out, iB_out;
  wire[15:0] add_AB_out, add_iAB_out;
  wire[15:0] sub_AB_out, sub_iAB_out;
  wire[15:0] mul_AB_out, mul_iAB_out;
  wire[15:0] div_AB_out, div_iAB_out;

  Multiplication mult(A_out, B_out, iA_out, iB_out, complx_control, clk, mul_AB_out, mul_iAB_out);
  Division div(A_out, B_out, iA_out, iB_out, complx_control, clk, div_AB_out, div_iAB_out);
  Addition add(A_out, B_out, iA_out, iB_out, clk, add_AB_out, add_iAB_out);
  Substract sub(A_out, B_out, iA_out, iB_out, clk, sub_AB_out, sub_iAB_out);
  mux_complx mx_cmplx(A_in, B_in, iA_in, iB_in, complx_control, A_out, B_out, iA_out, iB_out);
  mux_math mx_mth(add_AB_out, add_iAB_out, sub_AB_out, sub_iAB_out, mul_AB_out, mul_iAB_out, div_AB_out, div_iAB_out, math_control, AB_out, iAB_out, clk);

  assign clk = clk_reg;

  initial

  begin

    complx_control = 0;
    math_control = 0;
    A_in = 10;
    B_in = 8;
    iA_in = 4;
    iB_in = 2;


    #50 A_in = 14;
    math_control = 1;
    B_in = 7;
    iA_in = 5;
    iB_in = 2;


    #50 A_in = 8;
    math_control = 2;
    B_in = 6;
    iA_in = 5;
    iB_in = 3;


    #50 A_in = 11;
    math_control = 3;
    B_in = 8;
    iA_in = 7;
    iB_in = 3;

// -----------------------------------
    #45 complx_control = 1;
    #5 math_control = 0;
    A_in = 10;
    B_in = 8;
    iA_in = 4;
    iB_in = 2;


    #50 A_in = 14;
    math_control = 1;
    B_in = 7;
    iA_in = 5;
    iB_in = 2;


    #50 A_in = 8;
    math_control = 2;
    B_in = 6;
    iA_in = 5;
    iB_in = 3;


    #50 A_in = 11;
    math_control = 3;
    B_in = 8;
    iA_in = 7;
    iB_in = 3;

  end


  initial
  begin
    clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
    #7 clk_reg = 1'b1;
    #7 clk_reg = 1'b0;
  end
endmodule
