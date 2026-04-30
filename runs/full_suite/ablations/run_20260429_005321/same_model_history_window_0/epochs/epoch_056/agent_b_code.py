def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    obs=set(tuple(p) for p in observation.get("obstacles",[]))
    resources=[tuple(p) for p in observation.get("resources",[])]
    moves=[(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move=moves[4]; best_val=-10**18

    def man(a,b,c,d):
        return abs(a-c)+abs(b-d)

    # If we are already on a resource, stay (often best to collect)
    if (sx,sy) in set(resources):
        return [0,0]

    def cell_ok(x,y):
        return 0<=x<w and 0<=y<h and (x,y) not in obs

    for dx,dy in moves:
        nx,ny=sx+dx,sy+dy
        if not cell_ok(nx,ny):
            continue
        # Immediate preference to stepping onto a resource
        step_bonus=1e6 if (nx,ny) in set(resources) else 0.0
        # Score: try to reach resources where we are closer than opponent
        # Use simple Manhattan distance; deterministic and fast.
        val=step_bonus
        for rx,ry in resources:
            ds=man(nx,ny,rx,ry)
            do=man(ox,oy,rx,ry)
            # Encourage resources where opponent is farther; also slightly prefer closer ones.
            val += (do-ds)*10.0 - ds*0.2
        # If no resources, or all equal, fall back to moving away from opponent
        if not resources:
            val = (man(nx,ny,ox,oy))*1.0 - 0.05*(abs(nx-(w-1)/2)+abs(ny-(h-1)/2))
        if val>best_val+1e-9:
            best_val=val; best_move=[dx,dy]

    # Guarantee return
    return best_move if cell_ok(sx+best_move[0], sy+best_move[1]) else [0,0]