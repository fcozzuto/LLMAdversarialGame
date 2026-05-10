def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    ti = int(observation.get("turn_index", 0) or 0)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None
    fallback = (0, 0)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = corners[0 if ((ox + oy + ti) & 1) == 0 else 3]
        dx0 = 0 if tx == sx else (1 if tx > sx else -1)
        dy0 = 0 if ty == sy else (1 if ty > sy else -1)
        fallback = (dx0, dy0)

        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            return [dx if dx in (-1, 0, 1) else 0, dy if dy in (-1, 0, 1) else 0]

        return [fallback[0], fallback[1]]

    # Precompute opponent distances for each resource (static during this turn).
    opp_d = {}
    for rx, ry in resources:
        opp_d[(rx, ry)] = cheb(ox, oy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose the resource that maximizes our advantage after this move.
        local_best = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = opp_d[(rx, ry)]
            lead = do - ds  # positive => we are closer than opponent
            # Tie-break: prefer smaller ds (more likely to grab), then farther opponent (bigger do)
            val = (lead, -ds, do)
            if local_best is None or val > local_best[0]:
                local_best = (val, rx, ry)

        if local_best is None:
            continue
        val = local_best[0]
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_val is None:
        # If all legal moves are blocked, stay still.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]