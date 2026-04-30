def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Choose target resource where we are relatively closer than opponent.
    if resources:
        best_res = None
        best_score = None
        for r in resources:
            rs = dist2((sx, sy), r)
            ro = dist2((ox, oy), r)
            # Prefer resources we can reach first; tie-break by overall closeness.
            sc = (ro - rs, -rs)
            if best_score is None or sc > best_score:
                best_score = sc
                best_res = r
        tx, ty = best_res
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If next step is blocked, avoid it; if multiple, pick best by target distance and opponent pressure.
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Predict opponent tendency toward their nearest resource.
        if resources:
            opp_target = None
            opp_best = None
            for r in resources:
                d = dist2((ox, oy), r)
                if opp_best is None or d < opp_best:
                    opp_best = d
                    opp_target = r
            px, py = opp_target
            # Prefer to reduce chance they can take target by moving toward it ourselves.
            opp_dist_after = dist2((px, py), (nx, ny))
            opp_press = opp_dist_after
        else:
            opp_press = 0

        # Main objective: minimize distance to our target.
        d_to_target = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)

        # Secondary: keep away from obstacles (prefer cells with more free neighbors).
        free_neighbors = 0
        for adx, ady in moves:
            ex, ey = nx + adx, ny + ady
            if inb(ex, ey) and (ex, ey) not in obstacles:
                free_neighbors += 1

        val = (d_to_target, opp_press, -free_neighbors, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]