def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]); obstacles=set(tuple(p) for p in observation.get("obstacles",[]))
    if not resources: return [0,0]
    def dist(a,b): 
        dx=abs(a[0]-b[0]); dy=abs(a[1]-b[1]); 
        return dx if dx>dy else dy  # chebyshev for 8-neigh with 1 step
    def inb(x,y): return 0<=x<w and 0<=y<h
    # Pick a target resource we are more likely to reach first
    best_res=resources[0]; best_key=None
    for r in resources:
        sd=dist((sx,sy),r); od=dist((ox,oy),r)
        key=(sd-od, sd)  # smaller is better: prioritize resources closer than opponent
        if best_key is None or key<best_key: best_key=key; best_res=r
    tx,ty=best_res
    # Candidate moves: all deltas in {-1,0,1}^2
    deltas=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move=[0,0]; best_score=None
    for dx,dy in deltas:
        nx,ny=sx+dx,sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles: 
            continue
        sd2=dist((nx,ny), (tx,ty))
        od2=dist((ox,oy), (tx,ty))
        # Small tie-breakers: avoid stepping into obstacle-adjacent cells, and slightly prefer moving toward opponent
        adj_pen=0
        for ax,ay in ((nx+1,ny),(nx-1,ny),(nx,ny+1),(nx,ny-1),(nx+1,ny+1),(nx+1,ny-1),(nx-1,ny+1),(nx-1,ny-1)):
            if inb(ax,ay) and (ax,ay) in obstacles: adj_pen+=1
        closer_opp = dist((nx,ny),(ox,oy)) - dist((sx,sy),(ox,oy))
        score = sd2 - 0.9*od2 + 0.6*adj_pen + 0.05*closer_opp
        if best_score is None or score<best_score:
            best_score=score; best_move=[dx,dy]
    return best_move