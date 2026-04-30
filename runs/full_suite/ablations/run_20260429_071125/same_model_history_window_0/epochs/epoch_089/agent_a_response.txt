def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]) or []
    obstacles=set(tuple(p) for p in (observation.get("obstacles",[]) or []))
    obs=tuple([sx,sy])
    # deterministic list for tie-breaking preference
    deltas=[(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist2(a,b): dx=a[0]-b[0]; dy=a[1]-b[1]; return dx*dx+dy*dy
    def inside(x,y): return 0<=x<w and 0<=y<h
    # choose target resource with opponent-aware advantage
    rem=observation.get("remaining_resource_count",len(resources))
    if resources:
        # strategy change: when not improving, target max (opp closer than us => avoid, else exploit)
        best=None; best_key=None
        for r in resources:
            rx,ry=r
            sd=dist2((sx,sy),(rx,ry))
            od=dist2((ox,oy),(rx,ry))
            # If few resources remain, prioritize nearest to us; otherwise prioritize swing in tempo vs opponent
            if rem<=4:
                key=(0, sd, abs(rx-(w-1-sx))+abs(ry-(h-1-sy)), rx, ry)
            else:
                advantage=od - sd  # positive => we are closer
                # also slightly prefer resources closer to center to avoid long edge races
                center=( (w-1)/2.0, (h-1)/2.0 )
                cd=(rx-center[0])**2+(ry-center[1])**2
                key=(-advantage, cd, sd, rx, ry)
            if best_key is None or key<best_key:
                best_key=key; best=(rx,ry)
        tx,ty=best
    else:
        # no resources: move to intercept/block by heading toward opponent
        tx,ty=ox,oy
    # pick best feasible move that decreases distance to target; if tie, deterministic ordering
    best_move=(0,0); best_score=None
    for dx,dy in deltas:
        nx,ny=sx+dx,sy+dy
        if not inside(nx,ny): continue
        if (nx,ny) in obstacles: continue
        score=dist2((nx,ny),(tx,ty))
        # prefer staying if equal score to reduce churn
        tiebreak=(score, 0 if (dx,dy)==(0,0) else 1, abs(dx)+abs(dy), dx, dy)
        if best_score is None or tiebreak<best_score:
            best_score=tiebreak; best_move=(dx,dy)
    return [int(best_move[0]), int(best_move[1])]