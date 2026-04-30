def choose_move(observation):
    w=observation.get('grid_width',8); h=observation.get('grid_height',8)
    sx,sy=observation['self_position']; ox,oy=observation['opponent_position']
    resources=observation.get('resources',[]) or []
    obstacles=set(tuple(p) for p in (observation.get('obstacles',[]) or []))
    def cheb(a,b,c,d): 
        dx=abs(a-c); dy=abs(b-d); 
        return dx if dx>dy else dy
    target=None
    best_margin=-10**9
    if resources:
        for rx,ry in resources:
            ds=cheb(sx,sy,rx,ry); do=cheb(ox,oy,rx,ry)
            margin=do-ds  # positive means we are closer or can arrive first
            if margin>best_margin:
                best_margin=margin; target=(rx,ry)
        if best_margin<0:
            # if opponent is closer to everything, still go to the best "almost" target (smallest ds)
            target=None; best_ds=10**9
            for rx,ry in resources:
                ds=cheb(sx,sy,rx,ry)
                if ds<best_ds:
                    best_ds=ds; target=(rx,ry)
    else:
        target=(sx,sy)
    def in_bounds(x,y): return 0<=x<w and 0<=y<h
    deltas=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move=(0,0); best_val=-10**18
    for dx,dy in deltas:
        nx=sx+dx; ny=sy+dy
        if not in_bounds(nx,ny): 
            continue
        if (nx,ny) in obstacles:
            continue
        d_t=cheb(nx,ny,target[0],target[1])
        d_o=cheb(nx,ny,ox,oy)
        # prefer reaching target, discourage moving toward opponent, and prefer leaving obstacles behind
        val=-(10*d_t) + (2*d_o)
        # slight preference for staying if equally good
        if (dx,dy)==(0,0): val+=0.01
        if val>best_val:
            best_val=val; best_move=(dx,dy)
    return [int(best_move[0]), int(best_move[1])]