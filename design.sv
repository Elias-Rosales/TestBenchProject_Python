module Modular1(x,y,s,m); //dawd
  input x,y,s; //awda
  output m; //dwwd
  wire w1,w2,w3;

  Not_Gate U1(s,w1);//adawd
  And_Gate U2(x,w1,w2);//Awdawd
  And_Gate U3(s,y,w3);//grdgrd
  Or_Gate U4(w2,w3,m);  //awaw
endmodule