module Lab6_1_1 (clk, clr, input1, output1, state);
  input clk, clr, input1;
  output output1, state;
  reg output1;
  reg [3:0] state;
  /* Кодирование состояний автомата*/
  parameter [3:0] state_A=0, state_B=1, state_C=2, state_D=3, state_E=4, state_F=5, state_G=6, state_H=7, state_I=8;

  always @ (posedge clk or posedge clr)
    begin
      if (clr)
        state = state_A;
      else
        begin
      /*Определение следующего состояния автомата*/
          case(state)
            state_A:
              if (input1 == 0)
                state = state_B;
              else
                state = state_F;

            state_B:
              if (input1 == 0)
                state = state_C;
              else
                state = state_F;

            state_C:
              if (input1 == 0)
                state = state_D;
              else
                state = state_F;

            state_D:
              if (input1 == 0)
                state = state_E;
              else
                state = state_F;

            state_E:
              if (input1 == 1)
                state = state_F;

            state_F:
              if (input1 == 0)
                state = state_B;
              else
                state = state_G;

            state_G:
              if (input1 == 0)
                state = state_B;
              else
                state = state_H;

            state_H:
              if (input1 == 0)
                state = state_B;
              else
                state = state_I;

            state_I:
              if (input1 == 0)
                state = state_B;

            default:
              state = state_A;
          endcase
        end
    end
      /*Состояние выхода конечного автомата*/
  always @(state)
    begin
      case (state)
        state_A: output1 = 0;
        state_B: output1 = 0;
        state_C: output1 = 0;
        state_D: output1 = 0;
        state_E: output1 = 1;
        state_F: output1 = 0;
        state_G: output1 = 0;
        state_H: output1 = 0;
        state_I: output1 = 1;
        default: output1 = 0;
      endcase
    end
endmodule
