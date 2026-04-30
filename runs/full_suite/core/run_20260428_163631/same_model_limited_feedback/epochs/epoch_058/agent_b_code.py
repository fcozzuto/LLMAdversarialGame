def choose_move(observation):
    w=observation.get("grid_width",8); h=observation.get("grid_height",8)
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[])
    obstacles=set(tuple(p) for p in observation.get("obstacles",[]))
    def clamp(v,lo,hi): 
        return lo if v<lo else hi if v>hi else v
    def inb(x,y): return 0<=x<w and 0<=y<h
    def cheb(a,b,c,d): 
        dx=abs(a-c); dy=abs(b-d); return dx if dx>dy else dy
    if not resources:
        # fallback: step away from opponent slightly
        dx=0; dy=0
        for m in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)):
            nx=sx+m[0]; ny=sy+m[1]
            if not inb(nx,ny) or (nx,ny) in obstacles: 
                continue
            if cheb(nx,ny,ox,oy)>cheb(sx,sy,ox,oy):
                dx,dy=m
                break
        return [int(dx),int(dy)]
    # strategy change: contest resources where opponent is closer, aiming to block/steal
    best=None; best_val=-10**9
    for rx,ry in resources:
        myd=cheb(sx,sy,rx,ry); opd=cheb(ox,oy,rx,ry)
        # prioritize resources where I can catch up or already be closer
        # also slightly prefer nearer absolute distance to finish quickly
        val=(opd-myd)*3 - myd - (0 if (rx,ry) not in obstacles else 50)
        if myd==0: val=10**6
        if val>best_val:
            best_val=val; best=(rx,ry)
    tx,ty=best
    # choose move that reduces my distance to target, but if opponent is very near target, bias to interception
    opp_near = 1 if cheb(ox,oy,tx,ty)<=1 else 0
    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    curd=cheb(sx,sy,tx,ty)
    best_move=(0,0); best_score=-10**9
    for dx,dy in moves:
        nx=sx+dx; ny=sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles: 
            continue
        myd=cheb(nx,ny,tx,ty)
        # block pressure: if opponent close, try to make my next position reduce opponent distance too (to contest)
        opd=cheb(ox,oy,tx,ty)
        step_to_opp=cheb(nx,ny,ox,oy)
        score=-(myd*2)
        score += (curd-myd)*4
        if opp_near:
            score += (opd - cheb(ox,oy,tx,ty))*0  # stable
            score += -step_to_opp  # keep away from swapping too much
            score += (cheb(nx,ny,tx,ty)==0)*100000
        # obstacle/edge penalty: discourage staying unless needed
        score -= (1 if dx==0 and dy==0 else 0)*0.2
        if score>best_score:
            best_score=score; best_move=(dx,dy)
    return [int(best_move[0]),int(best_move[1])]