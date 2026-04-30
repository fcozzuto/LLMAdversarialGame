def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set((p[0],p[1]) for p in observation["obstacles"])
    dirs=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0<=x<w and 0<=y<h
    def dist2(a,b,c,d): dx=a-c; dy=b-d; return dx*dx+dy*dy
    def best_target(parity):
        if not resources: return None
        if parity==0:
            best=None; bestv=None
            for rx,ry in resources:
                sv=dist2(sx,sy,rx,ry)
                ov=dist2(ox,oy,rx,ry)
                v=sv - 0.75*ov
                if bestv is None or v<bestv: bestv=v; best=(rx,ry)
            return best
        else:
            best=None; bestv=None
            for rx,ry in resources:
                v=dist2(ox,oy,rx,ry) - dist2(sx,sy,rx,ry)
                if bestv is None or v>bestv: bestv=v; best=(rx,ry)
            return best
    target=best_target(observation["turn_index"]%2)
    if target is None:
        return [0,0]
    tx,ty=target
    best_move=(0,0); best_score=None
    for dx,dy in dirs:
        nx=sx+dx; ny=sy+dy
        if not inb(nx,ny): continue
        if (nx,ny) in obstacles: score=-10**18
        else:
            s_to=dist2(nx,ny,tx,ty)
            o_to=dist2(ox,oy,tx,ty)
            on_res=1 if (nx,ny) in set((p[0],p[1]) for p in resources) else 0
            opp_close=dist2(nx,ny,ox,oy)
            score = -s_to + 0.6*o_to - 0.05*opp_close + 2.0*on_res
        if best_score is None or score>best_score:
            best_score=score; best_move=(dx,dy)
    return [int(best_move[0]), int(best_move[1])]