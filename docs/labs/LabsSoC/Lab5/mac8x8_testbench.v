module mac8x8_testbench;
    reg[7:0] a_reg,b_reg;
    reg clk_reg, clr_reg;
    wire[7:0] a,b;
    wire[15:0] c;
    wire clk, clr;
    wire[31:0] acc;

    mac8x8 mac(a, b, clk, clr, acc);

    initial
    begin
        a_reg = 1;
        #50 a_reg = 5;
        #50 a_reg = 1;
        #50 a_reg = 5;
        #50 a_reg = 1;
        #50 a_reg = 2;
        #50 a_reg = 4;
        #50 a_reg = 2;
        #50 a_reg = 4;
    end

    initial
    begin
        b_reg = 1;
        #100 b_reg = 10;
        #100 b_reg = 11;
        #100 b_reg = 20;
        #100 b_reg = 15;
    end

    initial
    begin
        clr_reg = 1'b0;
        #240 clr_reg = 1'b1;
    end

    initial
    begin
        clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
        #20 clk_reg = 1'b1;
        #20 clk_reg = 1'b0;
    end

    assign a = a_reg;
    assign b = b_reg;
    assign clk = clk_reg;
    assign clr = clr_reg;

endmodule
