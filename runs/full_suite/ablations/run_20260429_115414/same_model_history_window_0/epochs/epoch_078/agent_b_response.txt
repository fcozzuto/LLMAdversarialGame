def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]) or []
    obstacles=set(tuple(p) for p in (observation.get("obstacles",[]) or []))
    opp= (ox,oy)
    deltas=[(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    def inside(x,y): return 0<=x<w and 0<=y<h
    def dist(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
    # Choose a resource with preference for being closer than opponent, and with tiebreak by position.
    if resources:
        cand=[]
        for r in resources:
            r=tuple(r)
            ds=dist((sx,sy),r)
            do=dist(opp,r)
            cand.append((ds - 0.55*do, r[0], r[1], r))
        cand.sort()
        targets=[c[-1] for c in cand]
    else:
        targets=[]
    targets = targets[:6] if targets else [(0,0)]
    # Evaluate moves against best target found among top candidates.
    best=None
    for dx,dy in deltas:
        nx,ny=sx+dx,sy+dy
        if not inside(nx,ny) or (nx,ny) in obstacles:
            nx,ny=sx,sy
        # For each move, pick the best target it can approach.
        move_score=1e9
        for t in targets:
            ds=dist((nx,ny),t)
            do=dist((nx,ny),opp)
            # minimize ds; maximize do
            score=ds - 0.25*do
            if score < move_score: move_score=score
        # tie-break deterministically: prefer larger opponent distance, then smaller ds, then dx,dy
        # Convert move_score into components.
        # Recompute for the chosen best target for stable tie-break
        if targets:
            t=min(targets, key=lambda r: (dist((nx,ny),r)-0.25*dist((nx,ny),opp), r[0], r[1]))
            ds=dist((nx,ny),t); do=dist((nx,ny),opp)
        else:
            ds=0; do=0
        key=(move_score, -do, ds, dx, dy)
        if best is None or key < best[0]:
            best=(key,[dx,dy])
    return best[1] if best is not None else [0,0]