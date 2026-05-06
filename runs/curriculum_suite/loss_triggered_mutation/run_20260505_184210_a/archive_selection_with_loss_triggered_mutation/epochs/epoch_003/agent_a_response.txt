def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # Target selection: go for resources we can reach earlier (or at least contest).
    if resources:
        best = None
        for rx, ry in resources:
            d_s = dist((sx, sy), (rx, ry))
            d_o = dist((ox, oy), (rx, ry))
            # Prefer earlier arrival; tie-break by closer and more "central" to break ties deterministically.
            score = (d_s - d_o, d_s, -abs(rx - (w-1)/2) - abs(ry - (h-1)/2), rx, ry)
            if best is None or score < best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        # If no visible resources, contest the midpoint between both agents.
        tx, ty = (sx + ox) // 2, (sy + oy) // 2

    # If target is blocked, don't chase blindly: recompute a safer nearby waypoint.
    def best_waypoint(cx, cy):
        candidates = [(tx, ty), ((tx+sx)//2, (ty+sy)//2), (sx, sy)]
        for wx, wy in candidates:
            if 0 <= wx < w and 0 <= wy < h and (wx, wy) not in obstacles:
                return wx, wy
        # Fallback: nearest free cell around current position.
        for rdx in (-1,0,1):
            for rdy in (-1,0,1):
                nx, ny = cx+rdx, cy+rdy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return nx, ny
        return cx, cy

    tx, ty = best_waypoint(sx, sy)

    # Move selection: minimize distance to target; avoid stepping into opponent's immediate neighborhood.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dn = dist((nx, ny), (tx, ty))
        do = dist((ox, oy), (nx, ny))
        # Penalty for being adjacent (including diagonal) to opponent, unless it still improves target distance a lot.
        adjacent = max(abs(nx-ox), abs(ny-oy)) <= 1
        # Also reward moves that keep/restore advantage on the target if target exists.
        if resources:
            adv_now = dist((ox, oy), (tx, ty)) - dist((nx, ny), (tx, ty))
        else:
            adv_now = 0
        val = (dn, 0 if not adjacent else 1, -adv_now, -do, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move