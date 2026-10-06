
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <set>
#include <algorithm>
#include <climits>
using namespace std;
const unsigned unitb[22]={0,1,3,0,8,0,24,32,160,160,3,24,5,72,288,8200,1026,16416,6,16640,131616,0};
const int edgep[89][2]={{0,3},{0,4},{0,5},{0,21},{1,6},{1,13},{1,14},{2,6},{2,17},{1,3},{3,5},{3,8},{2,4},{4,5},{4,20},{1,5},{2,5},{5,6},{6,14},{6,17},{6,18},{0,7},{3,7},{7,10},{1,8},{8,13},{8,16},{0,9},{4,9},{9,12},{3,10},{8,10},{10,15},{0,11},{7,11},{9,11},{4,12},{12,20},{13,14},{13,19},{14,18},{8,15},{15,16},{13,16},{16,19},{17,18},{2,20},{7,17},{7,19},{8,20},{9,14},{10,12},{10,18},{11,13},{12,18},{4,15},{2,16},{17,19},{0,6},{0,8},{0,20},{1,17},{1,19},{2,14},{2,3},{3,14},{3,16},{1,4},{4,17},{5,13},{5,18},{1,7},{4,7},{7,15},{6,8},{2,9},{3,9},{5,10},{10,13},{5,11},{10,11},{11,12},{5,12},{13,18},{1,15},{15,19},{14,16},{6,20},{6,21}};
const vector<int> memberships[22]={{0,1,3,4},{1,2,4,5,6},{3,4,6},{0,1,2,4,5},{0,3,4},{0,1,3,4,5,6},{4,5,6},{0,1},{1,2,5},{0,3},{1,2},{0},{3},{2,5},{5,6},{2},{2},{6},{6},{},{3},{}};
const vector<int> costs[22]={{},{},{},{0,9,64},{1,12,67},{2,10,13,15,16},{4,7,17,58},{21,22,71,72},{11,24,59,74},{27,28,75,76},{23,30,31,77},{33,34,35,79,80},{29,36,51,81,82},{5,25,53,69,78},{6,18,38,50,63,65},{32,41,55,73,84},{26,42,43,56,66,86},{8,19,47,61,68},{20,40,45,52,54,70,83},{39,44,48,57,62,85},{14,37,46,49,60,87},{3,88}};
const int window_end[7]={11,10,16,20,6,14,18};
const int tri[3]={0,6,21};
long long coeff[89],best=LLONG_MIN,nodes=0,leaves=0,maxcount=0;
int col[22],cnt[7][5]={},np[7]={};unsigned classes[5]={};
vector<array<int,22>> solutions;set<pair<unsigned long long,unsigned long long>> signatures;
void dfs(int i,int top,long long score){
 ++nodes;
 if(i==22){
  ++leaves;
  if(score>best){best=score;maxcount=0;solutions.clear();signatures.clear();}
  if(score==best){++maxcount;if(solutions.size()<40){
   unsigned long long lo=0,hi=0;for(int j=0;j<89;++j)if(col[edgep[j][0]]==col[edgep[j][1]]){if(j<64)lo|=1ULL<<j;else hi|=1ULL<<(j-64);}
   if(signatures.insert({lo,hi}).second){array<int,22>w;copy(col,col+22,w.begin());solutions.push_back(w);}
  }}return;
 }
 for(int c=0;c<min(5,top+2);++c){
  if(unitb[i]&classes[c])continue;col[i]=c;
  if(i==max({tri[0],tri[1],tri[2]}) && int(col[tri[0]]==col[tri[1]])+int(col[tri[2]]==col[tri[1]])-int(col[tri[0]]==col[tri[2]])!=1)continue;
  bool bad=false;for(int t:memberships[i])if(np[t]+cnt[t][c]>2||(window_end[t]==i&&np[t]+cnt[t][c]!=2)){bad=true;break;}if(bad)continue;
  for(int t:memberships[i]){np[t]+=cnt[t][c];++cnt[t][c];}classes[c]|=1u<<i;
  long long inc=0;for(int j:costs[i])if(col[edgep[j][0]]==c)inc+=coeff[j];dfs(i+1,max(top,c),score+inc);
  classes[c]^=1u<<i;for(int t:memberships[i]){--cnt[t][c];np[t]-=cnt[t][c];}
 }
}
int main(int argc,char**argv){if(argc!=2)return 2;ifstream f(argv[1]);for(auto &x:coeff)if(!(f>>x))return 3;dfs(0,-1,0);
 cout<<"{\"maximum\":"<<best<<",\"nodes\":"<<nodes<<",\"leaves\":"<<leaves<<",\"maximizers\":"<<maxcount<<",\"words\":[";
 for(size_t i=0;i<solutions.size();++i){if(i)cout<<',';cout<<'"';for(int c:solutions[i])cout<<c;cout<<'"';}cout<<"]}\n";
}
