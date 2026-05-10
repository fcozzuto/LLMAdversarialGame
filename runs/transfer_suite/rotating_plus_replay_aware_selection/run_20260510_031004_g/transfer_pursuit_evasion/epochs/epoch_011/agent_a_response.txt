def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role)
    if not is_pursuer and (("pursuer" in opponent_role) or ("pursuit" in opponent_role)):
        is_pursuer = False
    if "evader" in self_role:
        is_pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def free_neighbors(nx, ny):
        cnt = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            tx, ty = nx + dx, ny + dy
            if valid(tx, ty):
                cnt += 1
        return cnt

    def corner_dist_score(nx, ny):
        # For evader: prefer farthest corner; for pursuer: prefer closest corner when ties happen.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        d = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners) if not is_pursuer else \
            min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
        return d

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        neigh = free_neighbors(nx, ny)
        corner_score = corner_dist_score(nx, ny)

        # New material strategy: route via "escape corridor" / "trap corridor" heuristic using edge attraction.
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        edge_pref = edge if not is_pursuer else -edge

        # Main objective: pursuer minimizes distance; evader maximizes distance.
        if is_pursuer:
            val = (-dist * 100) + (neigh * 2) + (corner_score * 0.5) + edge_pref
        else:
            val = (dist * 100) + (neigh * 2) + (corner_score * 0.5) + edge_pref

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]