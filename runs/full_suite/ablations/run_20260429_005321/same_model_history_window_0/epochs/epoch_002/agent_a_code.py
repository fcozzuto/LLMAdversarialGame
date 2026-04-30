def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation.get("resources",[]) or []
    obstacles=set(tuple(p) for p in (observation.get("obstacles",[]) or []))
    cand=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            nx,ny=sx+dx,sy+dy
            if 0<=nx<w and 0<=ny<h and (nx,ny) not in obstacles:
                cand.append((dx,dy))
    if not cand:
        return [0,0]

    if resources:
        best=None
        for rx,ry in resources:
            if (rx,ry) in obstacles:
                continue
            sd=abs(rx-sx)+abs(ry-sy)
            od=abs(rx-ox)+abs(ry-oy)
            # Prefer resources where we have relative advantage; break ties deterministically
            key=(od-sd, -sd, -(rx+ry), -rx, -ry)
            if best is None or key>best[0]:
                best=(key,rx,ry)
        _,tx,ty=best
        # Choose move minimizing distance to target, with deterministic tie-break
        bestm=None
        for dx,dy in cand:
            nx,ny=sx+dx,sy+dy
            d=abs(tx-nx)+abs(ty-ny)
            # tie-break favors moving toward decreasing coordinate sums (stable), then dx,dy
            key=(-d, -(nx+ny), -dx, -dy)
            if bestm is None or key>bestm[0]:
                bestm=(key,dx,dy)
        return [int(bestm[1]),int(bestm[2])]

    # No resources: head toward opponent to contest space (deterministic)
    bestm=None
    for dx,dy in cand:
        nx,ny=sx+dx,sy+dy
        d=abs(ox-nx)+abs(oy-ny)
        key=(-d, (nx-ny), -dx, -dy)
        if bestm is None or key>bestm[0]:
            bestm=(key,dx,dy)
    return [int(bestm[1]),int(bestm[2])]