def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]) or []
    obstacles=set((x,y) for x,y in (observation.get("obstacles",[]) or []))
    # valid moves
    moves=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            nx=sx+dx; ny=sy+dy
            if 0<=nx<w and 0<=ny<h and (nx,ny) not in obstacles:
                moves.append([dx,dy])
    if not moves:
        return [0,0]

    def dist(a,b): 
        return abs(a[0]-b[0])+abs(a[1]-b[1])

    # choose best resource by (how much sooner we get it vs opponent)
    best=None
    for rx,ry in resources:
        if (rx,ry) in obstacles: 
            continue
        ds=dist((sx,sy),(rx,ry))
        do=dist((ox,oy),(rx,ry))
        # minimize ds with bonus if opponent is farther; also slightly prefer closer total
        val=(ds - do, ds + 0.001*do)
        if best is None or val<best[0]:
            best=(val,(rx,ry))
    target=best[1] if best else (sx,sy)

    # attempt to move toward target; if opponent closer, bias toward blocking their path
    # compute opponent nearest resource target
    opp_best=None
    for rx,ry in resources:
        if (rx,ry) in obstacles:
            continue
        ds=dist((ox,oy),(rx,ry))
        if opp_best is None or ds<opp_best[0]:
            opp_best=(ds,(rx,ry))
    opp_target=opp_best[1] if opp_best else (ox,oy)
    d_self=dist((sx,sy),target)
    d_opp=dist((ox,oy),opp_target)
    # if opponent is closer to their target, try to step to a cell that increases their approach
    block_mode = bool(resources) and (dist((ox,oy),opp_target) <= dist((sx,sy),target))

    # score candidate moves
    tx,ty=target; ox_t,oy_t=opp_target
    def step_score(dx,dy):
        nx,ny=sx+dx,sy+dy
        # primary: get closer to chosen target
        ns=dist((nx,ny), (tx,ty))
        # secondary: avoid moving into opponent reach next step
        opp_next=dist((ox,oy),(nx,ny))
        # if blocking, prioritize increasing opponent's distance to their target
        if block_mode and (tx,ty)!=(sx,sy):
            no=dist((ox,oy),(ox_t,oy_t))
            nno=dist((ox,oy),(ox_t,oy_t))  # baseline (kept deterministic); use blocking by aiming at their line-ish
            # move should not worsen their distance too little: aim to reduce chance they can step closer after us
            opp_step=dist((ox,oy),(ox_t,oy_t)) - dist((nx,ny),(ox_t,oy_t))
            # smaller opp_step means we are not moving into their advantage
            return (ns, opp_next, -opp_step)
        return (ns, opp_next)

    best_move=None
    for dx,dy in moves:
        sc=step_score(dx,dy)
        if best_move is None or sc<best_move[0]:
            best_move=(sc,(dx,dy))
    return list(best_move[1])