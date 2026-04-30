def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    center_score = -cheb(sx, sy, int(cx + 0.5), int(cy + 0.5))

    if resources:
        best = None
        best_val = -10**9
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if md <= od:
                val = (od - md) * 10 - md
            else:
                val = -md * 2
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: drift toward center while keeping away from opponent.
        tx, ty = int(cx + 0.5), int(cy + 0.5)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Contest: prefer being closer to target than opponent; and avoid collisions.
        contest = (cheb(ox, oy, tx, ty) - d_to_t)
        # Mild center bias to adapt policy.
        c_bias = -cheb(nx, ny, int(cx + 0.5), int(cy + 0.5))
        score = -d_to_t * 5 + contest * 2 + d_to_o * 0.6 + c_bias * 0.2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]