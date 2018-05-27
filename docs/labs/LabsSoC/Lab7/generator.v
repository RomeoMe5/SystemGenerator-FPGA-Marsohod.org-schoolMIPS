module generator(A_in, B_in, iA_in, iB_in, clk, complx_control, math_control, );
input clk;
output [15:0] A_in, B_in, iA_in, iB_in;
reg [15:0] A_in, B_in, iA_in, iB_in;
output complx_control;
output math_control[1:0];

reg complx_control;
reg [1:0] math_control, inner_clk_cnt;
reg [25:0] counter;

initial
begin
 counter = 26'b0;
 complx_control = 1'b0;
 math_control = 2'b0;
 A_in = 10'd5;
 B_in = 10'd4;
 iA_in = 10'd3;
 iB_in = 10'd1;
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
                complx_control = 1'b1;
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