def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []); obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b):  # Chebyshev for 8-neighbor
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if resources:
        best_t = resources[0]; best_s = -10**18
        for rx, ry in resources:
            sd = dist((sx,sy),(rx,ry)); od = dist((ox,oy),(rx,ry))
            s = (od - sd)*100 - sd  # prefer being closer than opponent
            if s > best_s: best_s = s; best_t = (rx,ry)
    else:
        best_t = (ox, oy)  # no resources: hold position near center-ish via opponent distance
    tx, ty = best_t
    opp_d = dist((ox,oy),(sx,sy))
    cell_set = set(tuple(p) for p in resources)
    best_move = (0,0); best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx,ny),(tx,ty))
        score = -nd*10
        if (nx, ny) in cell_set:
            score += 1000
        new_opp_d = dist((nx,ny),(ox,oy))
        score += (new_opp_d - opp_d)*2  # keep away
        # slight bias to advance
        score += -(abs(nx-tx)+abs(ny-ty))*0.01
        if score > best_score:
            best_score = score; best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]