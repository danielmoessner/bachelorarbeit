method example1(x_input: int, y_input: int) 
requires x_input < y_input
{
    var x := x_input;
    var y := y_input;

    while(x < y) 
        invariant x - 16 <= y
    {
         if x < 0 {
            x := x + 7;
        } else {
            x := x + 10;
        }
        if y < 0 {
            y := y - 10;
        } else {
            y := y - 3;
        }
    }

    assert y <= x <= y + 16;
}