def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(a, b): return 0 <= a < w and 0 <= b < h
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    dirs = moves
    if not resources:
        dx = 0; dy = 0
        tx = (w-1)//2; ty = (h-1)//2
        if x < tx: dx = 1
        elif x > tx: dx = -1
        if y < ty: dy = 1
        elif y > ty: dy = -1
        return [dx, dy]
    best_target = None; best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        myd = abs(rx-x) + abs(ry-y)
        opd = abs(rx-ox) + abs(ry-oy)
        val = (opd - myd) * 10 - myd
        if best_val is None or val > best_val:
            best_val = val; best_target = (rx, ry)
    tx, ty = best_target if best_target is not None else ((w-1)//2, (h-1)//2)
    opp_block_x = ox; opp_block_y = oy
    best_move = (0, 0); best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles: 
            continue
        myd = abs(tx-nx) + abs(ty-ny)
        opd = abs(tx-opp_block_x) + abs(ty-opp_block_y)
        toward = -(myd)
        rel = (opd - myd) * 10
        center = - (abs(nx-(w-1)/2) + abs(ny-(h-1)/2)) * 0.1
        avoid_opp = - (abs(nx-ox) + abs(ny-oy)) * 0.01
        score = rel + toward + center + avoid_opp
        if best_score is None or score > best_score or (score == best_score and (dx,dy) < best_move):
            best_score = score; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]