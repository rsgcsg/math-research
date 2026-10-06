// Untrusted RUP dependency extractor. The Python verifier checks every output.
// No external SAT solver or claims of RAT support are used by this utility.
#include <algorithm>
#include <deque>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
struct Extractor {
    int nv, epoch=1, original=0, round=0;
    vector<vector<int>> clauses, deps, occurrence;
    vector<signed char> base, trial;
    vector<int> why, basewhy, stamp, mark;
    explicit Extractor(int n):nv(n),occurrence(2*n+2),base(n+1),trial(n+1),
        why(n+1,-1),basewhy(n+1,-1),stamp(n+1) {}
    int ix(int l) { return 2*abs(l)+(l<0); }
    int value(int v,bool t) { return t&&stamp[v]==epoch?trial[v]:base[v]; }
    int reason(int v,bool t) { return t&&stamp[v]==epoch?why[v]:basewhy[v]; }
    void assign(int l,int r,bool t,deque<int>&q) {
        int v=abs(l);
        if(t){stamp[v]=epoch;trial[v]=l>0?1:-1;why[v]=r;}
        else {base[v]=l>0?1:-1;basewhy[v]=r;}
        q.push_back(l);
    }
    int inspect(int id,bool t,deque<int>&q) {
        int free=0,lit=0;
        for(int x:clauses[id]) {
            int v=value(abs(x),t);
            if(v==(x>0?1:-1))return -1;
            if(!v){++free;lit=x;if(free>1)return -1;}
        }
        if(!free)return id;
        assign(lit,id,t,q);return -1;
    }
    int propagate(bool t,deque<int>&q) {
        while(!q.empty()){
            int l=q.front();q.pop_front();
            for(int id:occurrence[ix(-l)]){
                int c=inspect(id,t,q);if(c>=0)return c;
            }
        }
        return -1;
    }
    int store(const vector<int>&c,const vector<int>&d) {
        int id=clauses.size();clauses.push_back(c);deps.push_back(d);mark.push_back(0);
        for(int l:c){if(!l||abs(l)>nv)throw runtime_error("literal range");occurrence[ix(l)].push_back(id);}
        return id;
    }
    vector<int> dependencies(int cid,int skip,bool t) {
        ++round;vector<pair<int,int>> todo={{cid,skip}};vector<int> out;
        while(!todo.empty()){
            auto [id,v]=todo.back();todo.pop_back();
            if(id<0||mark[id]==round)continue;
            mark[id]=round;out.push_back(id);
            for(int l:clauses[id]){
                int w=abs(l);
                if(w!=v&&value(w,t)==(l>0?-1:1)){
                    int r=reason(w,t);if(r>=0)todo.push_back({r,w});
                }
            }
        }
        sort(out.begin(),out.end());return out;
    }
    vector<int> prove(const vector<int>&c) {
        ++epoch;deque<int>q;
        for(int l:c){
            int v=abs(l);if(v>nv||!v)throw runtime_error("fresh variable");
            int s=l>0?-1:1,old=value(v,true);
            if(old&&old!=s)return dependencies(reason(v,true),v,true);
            if(!old)assign(-l,-1,true,q);
        }
        int contradiction=propagate(true,q);
        if(contradiction<0)throw runtime_error("non-RUP addition (not certified)");
        return dependencies(contradiction,0,true);
    }
    void output(int empty,const string&path) {
        vector<int>todo={empty};vector<char>used(clauses.size(),false);
        while(!todo.empty()){
            int id=todo.back();todo.pop_back();if(used[id])continue;
            used[id]=true;for(int j:deps[id])todo.push_back(j);
        }
        ofstream f(path);if(!f)throw runtime_error("output open");
        f<<"{\"initial_clause_ids\":[";bool comma=false;int ic=0,ac=0;
        for(int i=0;i<original;i++)if(used[i]){
            if(comma)f<<",";f<<i+1;comma=true;++ic;
        }
        f<<"],\"rup_clauses\":[";comma=false;
        for(int i=original;i<(int)clauses.size();i++)if(used[i]){
            if(comma)f<<",";f<<"[";
            for(int j=0;j<(int)clauses[i].size();j++){if(j)f<<",";f<<clauses[i][j];}
            f<<"]";comma=true;++ac;
        }
        f<<"]}\n";cerr<<"EXTRACTED "<<ic<<" initial "<<ac<<" additions; needs independent verification\n";
    }
};
int main(int argc,char**argv) {
    try{
        if(argc!=4)throw runtime_error("usage: CNF proof.drup core.json");
        ifstream f(argv[1]);string line;int nv=0,nc=0;
        while(getline(f,line)){
            if(line.empty()||line[0]=='c')continue;
            if(line[0]=='p'){string a,b;istringstream ss(line);ss>>a>>b>>nv>>nc;break;}
        }
        if(nv<=0||nc<=0)throw runtime_error("invalid CNF header");
        Extractor e(nv);vector<int>c;int x;
        while(f>>x){if(!x){e.store(c,{});c.clear();}else c.push_back(x);}
        if(!c.empty()||(int)e.clauses.size()!=nc)throw runtime_error("CNF count");
        e.original=nc;deque<int>q;int conflict=-1;
        for(int id=0;id<nc;id++){conflict=e.inspect(id,false,q);if(conflict>=0)break;}
        if(conflict<0)conflict=e.propagate(false,q);
        if(conflict>=0){int z=e.store({},e.dependencies(conflict,0,false));e.output(z,argv[3]);return 0;}
        ifstream p(argv[2]);if(!p)throw runtime_error("proof open");
        int number=0,added=0;
        while(getline(p,line)){
            ++number;if(line.empty()||line[0]=='d'||line[0]=='c')continue;
            istringstream ss(line);c.clear();bool ended=false;
            while(ss>>x){if(!x){ended=true;break;}c.push_back(x);}
            if(!ended)throw runtime_error("unterminated proof record");
            sort(c.begin(),c.end());c.erase(unique(c.begin(),c.end()),c.end());
            bool taut=false;for(int l:c)if(binary_search(c.begin(),c.end(),-l))taut=true;
            if(taut)continue;
            vector<int> ds;
            try{ds=e.prove(c);}catch(exception&err){cerr<<"at proof line "<<number<<": ";throw;}
            int id=e.store(c,ds);++added;
            if(c.empty()){e.output(id,argv[3]);return 0;}
            conflict=e.inspect(id,false,q);if(conflict<0)conflict=e.propagate(false,q);
            if(conflict>=0){int z=e.store({},e.dependencies(conflict,0,false));e.output(z,argv[3]);return 0;}
            if(added%20000==0)cerr<<"processed additions: "<<added<<"\n";
        }
        // Omitted empty clause is allowed only when actually derivable by RUP.
        auto ds=e.prove({});int z=e.store({},ds);e.output(z,argv[3]);return 0;
    }catch(exception&err){cerr<<err.what()<<"\n";return 1;}
}
