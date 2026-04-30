def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((x, y) for x, y in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we are most ahead in distance (prefer larger (opp - self))
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key
    if best is None:
        # No resources seen: move toward center and away from opponent
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = (int(round(tx)), int(round(ty)))

    rx, ry = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue
        d_to_target = cheb(nx, ny, rx, ry)
        d_to_opp = cheb(nx, ny, ox, oy)
        val = (-(d_to_target * 100 + (0 if (nx, ny) == (rx, ry) else 0)),
               d_to_target,
               -d_to_opp,
               dx, dy)
        # Prefer strictly smaller distance to target, then larger distance to opponent
        key = (d_to_target, -d_to_opp, dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]