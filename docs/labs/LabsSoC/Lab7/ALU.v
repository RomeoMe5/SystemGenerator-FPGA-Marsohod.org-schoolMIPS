module Division(A_in, B_in, iA_in, iB_in, complx, clk, AB_out, iAB_out);
	input[15:0] A_in, B_in, iA_in, iB_in;
	input complx;
	input clk;
	output[15:0] AB_out, iAB_out;
	reg [15:0] AB_out, iAB_out, a_div, b_div, ia_div;
	wire[15:0] ab_out_reim, ab_out_imre, ab_out_re2, ab_out_im2, ab_out_re, ab_out_im, div_out, div_out_rem, idiv_out, idiv_out_rem;

	mul16x16 mul0(A_in, B_in, ab_out_re);
	mul16x16 mul1(iA_in, iB_in, ab_out_im);
	mul16x16 mul2(A_in, iB_in, ab_out_reim);
	mul16x16 mul3(iA_in, B_in, ab_out_imre);
	mul16x16 mul4(B_in, B_in, ab_out_re2);
	mul16x16 mul5(iB_in, iB_in, ab_out_im2);

	div16x16 div0(a_div, b_div, div_out, div_out_rem);
   div16x16 div1(ia_div, b_div, idiv_out, idiv_out_rem);

	always @(posedge clk)
	begin
		if (complx)
			begin
				a_div = ab_out_re + ab_out_im;
				b_div = ab_out_re2 + ab_out_im2;
				AB_out = div_out;
				ia_div = ab_out_imre - ab_out_reim;
				iAB_out = idiv_out;
			end
		else
			begin
				a_div = A_in;
				b_div = B_in;
				AB_out = div_out;
				iAB_out = div_out;
			end
	end
endmodule

module Multiplication(A_in, B_in, iA_in, iB_in, complx, clk, AB_out, iAB_out);
	input[15:0] A_in, B_in, iA_in, iB_in;
	input complx;
	input clk;
	output[15:0] AB_out, iAB_out;
	reg [15:0] AB_out, iAB_out;
	wire[15:0] ab_out_reim, ab_out_imre, ab_out_re, ab_out_im;

	mul16x16 mul0(A_in, B_in, ab_out_re);
	mul16x16 mul1(iA_in, iB_in, ab_out_im);
	mul16x16 mul2(A_in, iB_in, ab_out_reim);
	mul16x16 mul3(iA_in, B_in, ab_out_imre);

	always @(posedge clk)
	begin
		if (complx)
			begin
				AB_out = ab_out_re - ab_out_im;
				iAB_out = ab_out_imre + ab_out_reim;
			end
		else
			begin
				AB_out = ab_out_re;
				iAB_out = ab_out_im;
			end
	end
endmodule

module Addition(A_in, B_in, iA_in, iB_in, clk, AB_out, iAB_out);
	input[15:0] A_in, B_in, iA_in, iB_in;
	input clk;
	output[15:0] AB_out, iAB_out;
	reg[15:0] AB_out, iAB_out;
	wire[15:0] ab_out, iab_out;

	AU au0(A_in, B_in, ab_out, {3'b000}, clk);
	AU au1(iA_in, iB_in, iab_out, {3'b000}, clk);

	always @(posedge clk)
	begin
		AB_out = ab_out;
		iAB_out = iab_out;
	end
endmodule


module Substract(A_in, B_in, iA_in, iB_in, clk, AB_out, iAB_out);
	input[15:0] A_in, B_in, iA_in, iB_in;
	input clk;
	output[15:0] AB_out, iAB_out;
	reg[15:0] AB_out, iAB_out;
	wire[15:0] ab_out, iab_out;

	AU au0(A_in, B_in, ab_out, {3'b010}, clk);
	AU au1(iA_in, iB_in, iab_out, {3'b010}, clk);

	always @(posedge clk)
	begin
		AB_out = ab_out;
		iAB_out = iab_out;
	end
endmodule

module AU(A_in, B_in, Shift_output, AU_control, clk);
	input[15:0] A_in, B_in;
	input clk;
	input [2:0] AU_control;
	output[15:0] Shift_output;
	reg[15:0] AU_output, Shift_output;

	always @(AU_control, A_in, B_in)
	begin
		case (AU_control[2:1])
			0:AU_output = A_in + B_in;
			1:AU_output = A_in - B_in;
			2:AU_output = A_in & B_in;
			3:AU_output = A_in | B_in;
			default: AU_output = 0;
		endcase

		Shift_output = AU_output;
	end

//	always @(posedge clk)
//		if (AU_control[0]==1)
//			Shift_output = AU_output<<1;
//		else
//			Shift_output = AU_output;
endmodule //

module div16x16(A_in, B_in, AB_quo_out, AB_rem_out);
  input [15:0] A_in, B_in;
  output [15:0] AB_quo_out, AB_rem_out;
  reg [15:0] AB_quo_out, AB_rem_out, a1, b1, p1;
  integer i;

  always @(A_in, B_in)
  begin
    a1 = A_in;
    b1 = B_in;
    p1 = 0;
    for(i=0; i<16; i=i+1)
      begin
        p1 = {p1[14:0], a1[15]};
        a1[15:1] = a1[14:0];
        p1 = p1-b1;
        if (p1[15] == 1)
          begin
            a1[0] = 0;
            p1 = p1+b1;
          end
        else
          a1[0] = 1;
      end
		AB_quo_out = a1;
		AB_rem_out = p1;
  end

endmodule


module mul16x16(A_in, B_in, AB_out);
    input [15:0] A_in, B_in;
	 output [15:0] AB_out;
    wire [31:0] c_32;
    wire[15:0] q0, q1, q2, q3, add0_0, temp0;
    wire[23:0] temp1, temp2, temp3, add0_1, add1_0;

    mul8x8 mac0(A_in[7:0],B_in[7:0],q0);
    mul8x8 mac1(A_in[15:8],B_in[7:0],q1);
    mul8x8 mac2(A_in[7:0],B_in[15:8],q2);
    mul8x8 mac3(A_in[15:8],B_in[15:8],q3);

    assign temp0 ={8'b0,q0[15:8]};
    adder16x16 adder0_0(q1,temp0,add0_0);

    assign temp1 ={8'b0,q2};
    assign temp2 ={q3,8'b0};
    adder24x24 adder0_1(temp1,temp2,add0_1);

    assign temp3={8'b0,add0_0};
    adder24x24 adder1_0(temp3,add0_1,add1_0);

    assign c_32[7:0]=q0[7:0];
    assign c_32[31:8]=add1_0;
    assign AB_out = c_32[15:0];

endmodule

module mul8x8
(
    input [7:0] a,b,
    output [15:0] c
);
    wire[7:0] q0, q1, q2, q3, add0_0, temp0;
    wire[11:0] temp1, temp2, temp3, add0_1, add1_0;

    mul4x4 mac0(a[3:0],b[3:0],q0);
    mul4x4 mac1(a[7:4],b[3:0],q1);
    mul4x4 mac2(a[3:0],b[7:4],q2);
    mul4x4 mac3(a[7:4],b[7:4],q3);

    assign temp0 ={4'b0,q0[7:4]};
    adder8x8 adder0_0(q1,temp0,add0_0);

    assign temp1 ={4'b0,q2};
    assign temp2 ={q3,4'b0};
    adder12x12 adder0_1(temp1,temp2,add0_1);

    assign temp3={4'b0,add0_0};
    adder12x12 adder1_0(temp3,add0_1,add1_0);

    assign c[3:0]=q0[3:0];
    assign c[15:4]=add1_0;
endmodule


module mul4x4
(
    input [3:0] a,b,
    output [7:0] c
);
    wire[3:0] q0, q1, q2, q3, add0_0, temp0;
    wire[5:0] temp1, temp2, temp3, add0_1, add1_0;

    mul2x2 z0(a[1:0],b[1:0],q0);
    mul2x2 z1(a[3:2],b[1:0],q1);
    mul2x2 z2(a[1:0],b[3:2],q2);
    mul2x2 z3(a[3:2],b[3:2],q3);

    assign temp0 ={2'b0,q0[3:2]};
    adder4x4 adder0_0(q1,temp0,add0_0);

    assign temp1 ={2'b0,q2};
    assign temp2 ={q3,2'b0};
    adder6x6 adder0_1(temp1,temp2,add0_1);

    assign temp3={2'b0,add0_0};
    adder6x6 adder1_0(temp3,add0_1,add1_0);

    assign c[1:0]=q0[1:0];
    assign c[7:2]=add1_0;
endmodule

module mul2x2
(
    input [1:0] a,b,
    output [3:0] c
);
    wire[3:0] temp;

    assign c[0] = a[0]&b[0];
    assign temp[0] = a[1]&b[0];
    assign temp[1] = a[0]&b[1];
    assign temp[2] = a[1]&b[1];

    hadder2x2 adder1(temp[0], temp[1], c[1], temp[3]);
    hadder2x2 adder2(temp[2], temp[3], c[2], c[3]);
endmodule

module adder24x24
(
    input [23:0] a, b,
    output [23:0] s
);
    wire [23:0] c_wire;

    bitsum sum0(a[0], b[0], s[0], {1'b0}, c_wire[0]);
    bitsum sum1(a[1], b[1], s[1], c_wire[0], c_wire[1]);
    bitsum sum2(a[2], b[2], s[2], c_wire[1], c_wire[2]);
    bitsum sum3(a[3], b[3], s[3], c_wire[2], c_wire[3]);
    bitsum sum4(a[4], b[4], s[4], c_wire[3], c_wire[4]);
    bitsum sum5(a[5], b[5], s[5], c_wire[4], c_wire[5]);
    bitsum sum6(a[6], b[6], s[6], c_wire[5], c_wire[6]);
    bitsum sum7(a[7], b[7], s[7], c_wire[6], c_wire[7]);
    bitsum sum8(a[8], b[8], s[8], c_wire[7], c_wire[8]);
    bitsum sum9(a[9], b[9], s[9], c_wire[8], c_wire[9]);
    bitsum sum10(a[10], b[10], s[10], c_wire[9], c_wire[10]);
    bitsum sum11(a[11], b[11], s[11], c_wire[10], c_wire[11]);
    bitsum sum12(a[12], b[12], s[12], c_wire[11], c_wire[12]);
    bitsum sum13(a[13], b[13], s[13], c_wire[12], c_wire[13]);
    bitsum sum14(a[14], b[14], s[14], c_wire[13], c_wire[14]);
    bitsum sum15(a[15], b[15], s[15], c_wire[14], c_wire[15]);
    bitsum sum16(a[16], b[16], s[16], c_wire[15], c_wire[16]);
    bitsum sum17(a[17], b[17], s[17], c_wire[16], c_wire[17]);
    bitsum sum18(a[18], b[18], s[18], c_wire[17], c_wire[18]);
    bitsum sum19(a[19], b[19], s[19], c_wire[18], c_wire[19]);
    bitsum sum20(a[20], b[20], s[20], c_wire[19], c_wire[20]);
    bitsum sum21(a[21], b[21], s[21], c_wire[20], c_wire[21]);
    bitsum sum22(a[22], b[22], s[22], c_wire[21], c_wire[22]);
    bitsum sum23(a[23], b[23], s[23], c_wire[22], c_wire[23]);
endmodule


module adder16x16
(
    input [15:0] a, b,
    output [15:0] s
);
    wire [15:0] c_wire;

    bitsum sum0(a[0], b[0], s[0], {1'b0}, c_wire[0]);
    bitsum sum1(a[1], b[1], s[1], c_wire[0], c_wire[1]);
    bitsum sum2(a[2], b[2], s[2], c_wire[1], c_wire[2]);
    bitsum sum3(a[3], b[3], s[3], c_wire[2], c_wire[3]);
    bitsum sum4(a[4], b[4], s[4], c_wire[3], c_wire[4]);
    bitsum sum5(a[5], b[5], s[5], c_wire[4], c_wire[5]);
    bitsum sum6(a[6], b[6], s[6], c_wire[5], c_wire[6]);
    bitsum sum7(a[7], b[7], s[7], c_wire[6], c_wire[7]);
    bitsum sum8(a[8], b[8], s[8], c_wire[7], c_wire[8]);
    bitsum sum9(a[9], b[9], s[9], c_wire[8], c_wire[9]);
    bitsum sum10(a[10], b[10], s[10], c_wire[9], c_wire[10]);
    bitsum sum11(a[11], b[11], s[11], c_wire[10], c_wire[11]);
    bitsum sum12(a[12], b[12], s[12], c_wire[11], c_wire[12]);
    bitsum sum13(a[13], b[13], s[13], c_wire[12], c_wire[13]);
    bitsum sum14(a[14], b[14], s[14], c_wire[13], c_wire[14]);
    bitsum sum15(a[15], b[15], s[15], c_wire[14], c_wire[15]);
endmodule


module adder12x12
(
    input [11:0] a, b,
    output [11:0] s
);
    wire [11:0] c_wire;

    bitsum sum0(a[0], b[0], s[0], {1'b0}, c_wire[0]);
    bitsum sum1(a[1], b[1], s[1], c_wire[0], c_wire[1]);
    bitsum sum2(a[2], b[2], s[2], c_wire[1], c_wire[2]);
    bitsum sum3(a[3], b[3], s[3], c_wire[2], c_wire[3]);
    bitsum sum4(a[4], b[4], s[4], c_wire[3], c_wire[4]);
    bitsum sum5(a[5], b[5], s[5], c_wire[4], c_wire[5]);
    bitsum sum6(a[6], b[6], s[6], c_wire[5], c_wire[6]);
    bitsum sum7(a[7], b[7], s[7], c_wire[6], c_wire[7]);
    bitsum sum8(a[8], b[8], s[8], c_wire[7], c_wire[8]);
    bitsum sum9(a[9], b[9], s[9], c_wire[8], c_wire[9]);
    bitsum sum10(a[10], b[10], s[10], c_wire[9], c_wire[10]);
    bitsum sum11(a[11], b[11], s[11], c_wire[10], c_wire[11]);
endmodule


module adder8x8
(
    input[7:0] a, b,
    output[7:0] s
);
    wire[7:0] c_wire;

    bitsum sum0(a[0], b[0], s[0], {1'b0}, c_wire[0]);
    bitsum sum1(a[1], b[1], s[1], c_wire[0], c_wire[1]);
    bitsum sum2(a[2], b[2], s[2], c_wire[1], c_wire[2]);
    bitsum sum3(a[3], b[3], s[3], c_wire[2], c_wire[3]);
    bitsum sum4(a[4], b[4], s[4], c_wire[3], c_wire[4]);
    bitsum sum5(a[5], b[5], s[5], c_wire[4], c_wire[5]);
    bitsum sum6(a[6], b[6], s[6], c_wire[5], c_wire[6]);
    bitsum sum7(a[7], b[7], s[7], c_wire[6], c_wire[7]);
endmodule


module adder6x6
(
    input[5:0] a, b,
    output[5:0] s
);
    wire [5:0] c_wire;

    bitsum sum0(a[0], b[0], s[0], {1'b0}, c_wire[0]);
    bitsum sum1(a[1], b[1], s[1], c_wire[0], c_wire[1]);
    bitsum sum2(a[2], b[2], s[2], c_wire[1], c_wire[2]);
    bitsum sum3(a[3], b[3], s[3], c_wire[2], c_wire[3]);
    bitsum sum4(a[4], b[4], s[4], c_wire[3], c_wire[4]);
    bitsum sum5(a[5], b[5], s[5], c_wire[4], c_wire[5]);
endmodule


module adder4x4
(
    input[3:0] a, b,
    output[3:0] s
);
    wire [3:0] c_wire;

    bitsum sum0(a[0], b[0], s[0], {1'b0}, c_wire[0]);
    bitsum sum1(a[1], b[1], s[1], c_wire[0], c_wire[1]);
    bitsum sum2(a[2], b[2], s[2], c_wire[1], c_wire[2]);
    bitsum sum3(a[3], b[3], s[3], c_wire[2], c_wire[3]);
endmodule

module bitsum (A, B, S, Cin, Cout);
    input A, B, Cin;
    output S, Cout;

    wire A, B, S, Res;
    wire c1, c2, Cin, Cout;

    xor(Res, A, B);
    and(c1, A, B);
    xor(S, Cin, Res);
    and(c2, Cin, Res);
    or(Cout, c1, c2);
endmodule

module hadder2x2
(
    input a,b,
    output s, c
);
    assign s = a^b;
    assign c = a&b;
endmodule
