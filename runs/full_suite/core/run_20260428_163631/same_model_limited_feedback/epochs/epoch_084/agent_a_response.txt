def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]); obstacles=set(map(tuple,observation.get("obstacles",[])))
    if not resources:
        return [0,0]
    def dist(a,b,c,d):
        dx=a-c; dy=b-d
        return (dx*dx+dy*dy)
    # Pick a target resource the opponent is relatively far from (and we are closer to).
    bestT=None; bestScore=-10**18
    for rx,ry in resources:
        if (rx,ry) in obstacles: 
            continue
        sd=dist(sx,sy,rx,ry); od=dist(ox,oy,rx,ry)
        # Larger score = better: we are closer than opponent, and closer in absolute terms.
        score=(od - sd)*1000 - sd
        if score>bestScore:
            bestScore=score; bestT=(rx,ry)
    if bestT is None:
        bestT=tuple(resources[0])
    tx,ty=bestT
    moves=[(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # If we're already on target, try to stay or step away slightly from opponent to keep resource.
    if (sx,sy)==(tx,ty):
        best=[0,0]; bestV=-10**18
        for dx,dy in moves:
            nx=sx+dx; ny=sy+dy
            if nx<0 or nx>=w or ny<0 or ny>=h: 
                continue
            if (nx,ny) in obstacles: 
                continue
            v=0
            # Prefer staying when opponent is not adjacent
            opadj=abs(nx-ox)<=1 and abs(ny-oy)<=1
            v += 200 if not opadj else -50
            # Slightly reduce distance to nearest resource after (avoid getting lured)
            md=10**18
            for rx,ry in resources:
                if (rx,ry) in obstacles: 
                    continue
                d=dist(nx,ny,rx,ry)
                if d<md: md=d
            v += -md
            if v>bestV:
                bestV=v; best=[dx,dy]
        return best
    # Otherwise move toward target while avoiding obstacles and discouraging moving too close to opponent.
    best=[0,0]; bestV=-10**18
    for dx,dy in moves:
        nx=sx+dx; ny=sy+dy
        if nx<0 or nx>=w or ny<0 or ny>=h:
            continue
        if (nx,ny) in obstacles:
            continue
        sd=dist(nx,ny,tx,ty)
        # discourage stepping into opponent's neighborhood
        opp_close=abs(nx-ox)<=1 and abs(ny-oy)<=1
        # encourage blocking: if opponent also near target, try to reduce their distance less than ours
        od=dist(ox,oy,tx,ty)
        v=0
        v += -sd*10
        v += 400000 if (nx,ny)==(tx,ty) else 0
        v += -1500 if opp_close else 0
        # prefer making opponent slower at reaching the same target
        v += (od - dist(nx,ny,tx,ty))*200
        if v>bestV:
            bestV=v; best=[dx,dy]
    return [int(best[0]), int(best[1])]