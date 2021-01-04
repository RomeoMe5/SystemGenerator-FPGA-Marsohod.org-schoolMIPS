/*
Copyright (c) 2017- HSE University students
Dmitriy Pchelkin (hell03end) and Alexey Ivanov (DigiDon)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

*/
// ------------------------------------------------------------------------ //
// This 'v' file is created by HSE University System Builder.
// ------------------------------------------------------------------------ //

module marsohod2b_mmio_mips();

// --------------------------------------- //
//          REG/WIRE declarations          //
// --------------------------------------- //


    wire	clk	;
    wire	clkIn	 = CLK100MHZ;
    wire	rst_n	 = KEY0;
    wire	clkEnable	 = ~KEY1;
    wire[31:0]		regData;


// --------------------------------------- //
//            Structural coding            //
// --------------------------------------- //


    sm_top sm_top
    (
        .clkIn		(clkIn ),
        .rst_n		(rst_n ),
        .clkDevide		(4'b1000 ),
        .clkEnable		(clkEnable ),
        .clk		(clk ),
        .regAddr		(4'b0010 ),
        .regData		(regData )
    );


endmodule // marsohod2b_mmio_mips

// ------------------------------------------------------------------------ //
// End of 'v' file created by HSE University System Builder.
// ------------------------------------------------------------------------ //
