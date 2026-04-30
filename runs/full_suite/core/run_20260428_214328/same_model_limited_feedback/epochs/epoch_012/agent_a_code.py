def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set(tuple(p) for p in observation["obstacles"])
    # Candidate moves
    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0<=x<w and 0<=y<h
    def dist(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
    def avg_manh(x,y,pts):
        if not pts: return 0
        s=0
        for px,py in pts: s+=abs(px-x)+abs(py-y)
        return s/len(pts)
    # Select a target resource: prefer ones opponent can't reach sooner
    opp= (ox,oy)
    candidates=[]
    for r in resources:
        rx,ry=r
        if (rx,ry) in obstacles: continue
        d_self=dist((sx,sy),r)
        d_opp=dist(opp,r)
        # prefer resources that are strictly closer for us or at least not behind
        lead=(d_opp-d_self)
        candidates.append((lead,d_self,r))
    # If no resources, head to center
    if not candidates:
        target=(w//2,h//2)
    else:
        candidates.sort(key=lambda t:(-t[0],t[1],t[2][0],t[2][1]))
        # Choose among top few deterministically to vary strategy when behind
        top=candidates[:min(4,len(candidates))]
        # If we're behind on the best, take a resource where we are relatively less behind
        # Deterministic: pick best by lead, then by distance
        _,_,target=top[0]
    # Evaluate moves
    best=None
    for dx,dy in moves:
        nx=sx+dx; ny=sy+dy
        if not inb(nx,ny): nx,ny=sx,sy
        if (nx,ny) in obstacles: nx,ny=sx,sy
        # If we can collect now, prioritize
        collect=1 if (nx,ny)==tuple(target) else 0
        d_t=dist((nx,ny),target)
        d_o=dist((nx,ny),(ox,oy))
        # Obstacle proximity penalty (discourage stepping near obstacles)
        prox=0
        for ax,ay in obstacles:
            if abs(ax-nx)<=1 and abs(ay-ny)<=1: prox+=1
        score=0
        score += collect*1000
        score += -d_t*10
        score += d_o*2
        score += -prox*3
        # Small tie-break: prefer staying only if already best; otherwise deterministic order
        score += -abs(dx)*0.1 - abs(dy)*0.1
        if best is None or score>best[0]:
            best=(score,dx,dy)
    return [best[1],best[2]]