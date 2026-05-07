def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_value(px, py):
        best = None
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Primary: be closer than opponent (smaller sd-od). Secondary: closer to resource.
            s = (sd - od, sd)
            if best is None or s < best[0]:
                best = (s, (rx, ry))
        return best[0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_m = (10**9, 0, 0)
    target_val = cell_value(sx, sy)

    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        val = cell_value(nx, ny)
        # Small deterministic preference: if equal, prefer move that changes x first, then y.
        tie = (abs(dx), abs(dy))
        cand = (val[0]*100 + val[1], tie[0], tie[1])
        if cand < best_m:
            best_m = cand
            best_move = [dx, dy]

    # If somehow no move chosen (shouldn't happen), stay still.
    try:
        return best_move
    except UnboundLocalError:
        return [0, 0]