/*
 * 7-segment indicator counter
 */
module Seven (
    input [3:0] code_i,
    output reg [7:0] hg_o
);
    always @* begin
        case (code_i) // hgfedcba
            4'h0 : hg_o = ~8'b00111111;
            4'h1 : hg_o = ~8'b00000110;
            4'h2 : hg_o = ~8'b01011011;
            4'h3 : hg_o = ~8'b01001111;
            4'h4 : hg_o = ~8'b01100110;
            4'h5 : hg_o = ~8'b01101101;
            4'h6 : hg_o = ~8'b01111101;
            4'h7 : hg_o = ~8'b00000111;
            4'h8 : hg_o = ~8'b01111111;
            4'h9 : hg_o = ~8'b01101111;
            4'hA : hg_o = ~8'b01110111;
            4'hB : hg_o = ~8'b01111100;
            4'hC : hg_o = ~8'b00111001;
            4'hD : hg_o = ~8'b01011110;
            4'hE : hg_o = ~8'b01111001;
            4'hF : hg_o = ~8'b01110001;
            default:hg_o= ~8'b10000000;
        endcase
    end

endmodule
