def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if ("evad" in self_role) or self_role == "evader":
        mode = "evade"
    elif ("purs" in self_role) or self_role == "pursuer":
        mode = "pursue"
    else:
        mode = "pursue" if ("evad" in opponent_role) or opponent_role == "evader" else "evade"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neigh_free(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        md = abs(nx - ox) + abs(ny - oy)
        mobility = neigh_free(nx, ny)
        adj_wall = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obs:
                adj_wall += 1
        # Tie-break deterministically: prefer larger (mode-dependent) primary value, then mobility, then fewer wall adjacencies.
        if mode == "pursue":
            score = (-md, mobility, -adj_wall, -nx, -ny)
        else:
            score = (md, mobility, -adj_wall, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]