module Generate_Clk(clk, clk_gen);
  input clk;
  output clk_gen;  
  reg[25:0] counter;
  reg clk_gen;
  
  initial
  begin
    counter = 26'b0;
  end
  
  always @(posedge clk)
  begin
	 counter = counter + 1'b1;
    if(counter == 26'd25000000) //25000000
	 begin
        counter = 26'b0;
		  clk_gen = 1;
	 end
	 else
		clk_gen = 0;
  end
endmodule

module Generate(clk, DIN, clr_counter);
  input clk;
  output[15:0] DIN;
  output clr_counter;
  reg clr_counter;
  reg[25:0] counter;
  reg[15:0] DIN;
  reg[3:0] DIN_case;

  initial
  begin
    counter = 26'b0;
	 DIN_case = 4'b0;
	 clr_counter = 0;
  end

  always @(posedge clk)
  begin
    counter = counter + 1'b1;
	 if (counter == 26'd5)
	 begin
	   clr_counter = 1;
	   case (DIN_case)
		  4'd0: DIN[8:0] = 9'b001001111;
		  4'd1: DIN[8:0] = 9'b000000001;
		  4'd2: DIN[8:0] = 9'b010000001;
		  4'd3: DIN[8:0] = 9'b011000001;
		  default: DIN[8:0] = 9'b001001000;
		endcase
		DIN_case = DIN_case + 1'b1;
		counter = 26'b0;
	 end
	 else
	 clr_counter = 0;
  end
endmodule

module UserClk(clk, clk_out);
  input clk;
  output clk_out;
  wire clk_out;
  reg clk_out_reg;
  reg[25:0] counter;
  
  initial
  begin
	 counter = 26'b0;
	 clk_out_reg = 0;
  end
  
  always@(posedge clk)
  begin
	 counter = counter + 1'b1;
    if(counter == 26'd5)
      begin
        counter = 26'b0;
        clk_out_reg = 1'b1;
      end
    else
		clk_out_reg = 1'b0;
  end
  
  assign clk_out = clk_out_reg;
endmodule 
	
module AddSubG(G_en, A_in, Bus, math_op, clk, G_out);
  input clk, G_en, math_op;
  input[15:0] Bus, A_in;
  output[15:0] G_out;
  reg[15:0] G_out;

  always @(posedge clk)
    case (math_op)
      0: G_out = A_in + Bus;
      1: G_out = A_in - Bus;
      default: G_out = 16'b1;
    endcase
endmodule

module R_mem_reg(Bus, R_mem_en, clk, R_mem_out);
  input[15:0] Bus;
  input R_mem_en, clk;
  output[15:0] R_mem_out;
  reg[15:0] R_mem_out;

  always@(posedge clk)
  if (R_mem_en == 1)
    R_mem_out = Bus;
endmodule

module A_reg(A_en, Bus, clk, A_out);
  input clk, A_en;
  input[15:0] Bus;
  output[15:0] A_out;
  reg[15:0] A_out;

  always @(posedge clk)
    A_out = Bus;
endmodule

module Multiplexer(DIN, R_mem0, R_mem1, R_mem2, R_mem3, R_mem4, R_mem5, R_mem6, R_mem7,
G_in, R_chs, DIN_chs, G_chs, Bus);
  input[15:0] DIN, G_in;
  input[15:0] R_mem0, R_mem1, R_mem2, R_mem3, R_mem4, R_mem5, R_mem6, R_mem7;
  input[7:0] R_chs;
  input DIN_chs, G_chs;
  output[15:0] Bus;
  reg[15:0] Bus;

  always @(R_chs, G_chs, DIN_chs)
  begin
  if (G_chs == 1)
    Bus = G_in;
  else
    if (DIN_chs == 1)
	   Bus = DIN;
	 else
		 case (R_chs)
			8'd1: Bus = R_mem0;
			8'd2: Bus = R_mem1;
			8'd4: Bus = R_mem2;
			8'd8: Bus = R_mem3;
			8'd16: Bus = R_mem4;
			8'd32: Bus = R_mem5;
			8'd64: Bus = R_mem6;
			8'd128: Bus = R_mem7;
			default: Bus = 15'b1;
		 endcase
  end
endmodule

module Counter(clr_counter, clk, count);
  input clr_counter;
  input clk;
  output[2:0] count;
  reg[2:0] count;

  initial
  begin
    count = 3'b0;
  end

  always @(posedge clk)
  begin
    count = count + 1'b1;
    if (clr_counter == 1'b1)
	   count = 3'b0;
  end
endmodule

module Control_unit(R_mem_en, R_chs, DIN_chs, G_chs, A_en, G_en, IR, IR_en, math_op, counter);
  input[2:0] counter;
  input[8:0] IR;
  output[7:0] R_mem_en, R_chs;
  output A_en, G_en, DIN_chs, G_chs, math_op, IR_en;
  reg A_en, G_en, DIN_chs, G_chs, math_op, IR_en;
  reg [7:0] R_mem_en, R_chs;
  reg [1:0] IR_cnt;
  
  initial
  begin
    IR_cnt = 2'b0;
	 IR_en = 1;
  end

  function[7:0] R_def;
    input[2:0] IR_XXX;
    begin
      case (IR_XXX)
        3'd0: R_def = 8'b00000001;
        3'd1: R_def = 8'b00000010;
        3'd2: R_def = 8'b00000100;
        3'd3: R_def = 8'b00001000;
        3'd4: R_def = 8'b00010000;
        3'd5: R_def = 8'b00100000;
        3'd6: R_def = 8'b01000000;
        3'd7: R_def = 8'b10000000;
        default: R_def = 8'b0;
      endcase
    end
  endfunction

  always @(counter)
  begin
		 case (IR[8:6])
			3'd0:
			  if (counter == 3'd0)
			  begin
				 IR_cnt = 2'd1;
				 R_mem_en = R_def(IR[5:3]);
				 R_chs = R_def(IR[2:0]);
				 DIN_chs = 0;
				 G_chs = 0;
				 A_en = 0;
				 G_en = 0;
			  end
			  else
			  begin
				 R_chs = 8'b0;
				 R_mem_en = 8'b0;
			  end

			3'd1:
			  if (counter == 3'b0)
			  begin
				 IR_cnt = 2'd1;
				 R_mem_en = R_def(IR[5:3]);
				 R_chs = 8'b0;
				 DIN_chs = 1;
				 G_chs = 0;
				 A_en = 0;
				 G_en = 0;
			  end
			  else
			  begin
				 R_chs = 8'b0;
				 R_mem_en = 8'b0;
			  end

			3'd2:
			case (counter)
			  3'd0:
				 begin
					IR_cnt = 2'd3;
					R_mem_en = 8'b0;
					R_chs = R_def(IR[2:0]);
					DIN_chs = 0;
					G_chs = 0;
					A_en = 1;
					G_en = 0;
					math_op = 0;
				 end
			  3'd1:
				 begin
					IR_cnt = 2'd3;
					R_mem_en = 8'b0;
					R_chs = R_def(IR[5:3]);
					DIN_chs = 0;
					G_chs = 0;
					A_en = 0;
					G_en = 1;
				 end
			  3'd2:
				 begin
					IR_cnt = 2'd3;
					R_mem_en = R_def(IR[5:3]);
					R_chs = 8'b0;
					DIN_chs = 0;
					G_chs = 1;
					A_en = 0;
					G_en = 0;
				 end
			  default:
				 begin
					R_chs = 8'b0;
					R_mem_en = 8'b0;
				 end
			endcase

			3'd3:
			  case(counter)
			  3'd0:
				 begin
					IR_cnt = 2'd3;
					R_mem_en = 8'b0;
					R_chs = R_def(IR[2:0]);
					DIN_chs = 0;
					G_chs = 0;
					A_en = 1;
					G_en = 0;
					math_op = 1;
				 end
			  3'd1:
				 begin
					IR_cnt = 2'd3;
					R_mem_en = 8'b0;
					R_chs = R_def(IR[5:3]);
					DIN_chs = 0;
					G_chs = 0;
					A_en = 0;
					G_en = 1;
				 end
			  3'd2:
				 begin
					IR_cnt = 2'd3;
					R_mem_en = R_def(IR[5:3]);
					R_chs = 8'b0;
					DIN_chs = 0;
					G_chs = 1;
					A_en = 0;
					G_en = 0;
				 end
			  default:
				 begin
					R_chs = 8'b0;
					R_mem_en = 8'b0;
				 end
			  endcase

			default:
			  begin
				 IR_cnt = 2'b0;
				 R_mem_en = 8'b0;
				 R_chs = 8'b0;
				 DIN_chs = 0;
				 G_chs = 0;
				 A_en = 0;
				 G_en = 1;
			  end
		 endcase
  end
endmodule

module IR_reg(clk, IR, DIN, IR_en);
  input clk, IR_en;
  input [15:0] DIN;
  output [8:0] IR;
  reg [8:0] IR;

  always @(posedge clk)
  begin
    if (IR_en == 1)
	   IR = DIN[8:0];
  end
endmodule
