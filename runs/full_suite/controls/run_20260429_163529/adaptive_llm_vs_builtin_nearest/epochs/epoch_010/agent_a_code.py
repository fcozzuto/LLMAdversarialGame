def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # drift toward center while keeping distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_move = [0, 0]
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            dist_opp = cheb(nx, ny, ox, oy)
            dist_ctr = cheb(nx, ny, cx, cy)
            score = (-dist_opp, dist_ctr)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # Choose target resource where we are relatively closer
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (-(ds - do), ds, rx, ry)  # prefer being closer than opponent; then nearest
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    cur_d = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # primary: reduce distance to target; secondary: avoid opponent; tertiary: keep moving
        val = (nd, -cheb(nx, ny, ox, oy), 0 if (dx == 0 and dy == 0) else 1, abs(nx - tx) + abs(ny - ty))
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    # If we somehow didn't find a valid move (should be rare), stay put
    if best_val is None:
        return [0, 0]
    return best_move