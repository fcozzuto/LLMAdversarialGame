def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("evad" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    def edge_penalty(x, y):
        # Encourage center for evader, allow edges for pursuer.
        return (min(x, w - 1 - x) + min(y, h - 1 - y))

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        neigh = free_neighbors_count(nx, ny)
        center = edge_penalty(nx, ny)

        if pursuer:
            # Primary: minimize distance. Secondary: prefer safer mobility.
            key = (d, -neigh, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2))
            # Deterministic tie-break: fixed move ordering already.
            better = best_key is None or key < best_key
        else:
            # Primary: maximize distance. Secondary: avoid dead-ends, and prefer center.
            key = (-d, -neigh, -center)
            better = best_key is None or key < best_key

        if better:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best