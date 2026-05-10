def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h

    best = None
    # Deterministic tie-break order via deltas list and score rounding.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        man = abs(ddx) + abs(ddy)

        # Exit count to avoid getting stuck/boundary traps
        exits = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if inside(ax, ay) and (ax, ay) not in obs:
                exits += 1

        # Boundary proximity penalty (helps against invalid moves keeping position)
        edge_pen = 0
        edge_pen += 1 if nx == 0 or nx == w - 1 else 0
        edge_pen += 1 if ny == 0 or ny == h - 1 else 0

        # If adjacent (in capture radius 0, still matters for pursuer), strong focus
        adjacent = 1 if man <= 1 else 0

        if is_pursuer:
            # minimize distance; prefer more exits; avoid edges; prioritize adjacency
            score = (-dist2) - 0.15 * man + 0.08 * exits - 0.35 * edge_pen + 2.5 * adjacent
        else:
            # maximize distance; prefer more exits; avoid edges; avoid stepping toward pursuer
            score = (dist2) + 0.15 * man + 0.08 * exits - 0.35 * edge_pen - 2.5 * adjacent

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]