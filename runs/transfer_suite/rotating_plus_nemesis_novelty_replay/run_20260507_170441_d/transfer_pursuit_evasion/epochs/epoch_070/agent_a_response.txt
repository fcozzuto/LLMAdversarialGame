def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role) or ("runner" in self_role)

    def mdist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d = mdist(nx, ny, ox, oy)

        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1

        if evader:
            # Prefer maximizing distance; if tied, move away on both axes; penalize obstacle-adjacency; avoid drifting into corner traps.
            awayx = 1 if (nx - ox) * (sx - ox) > 0 else 0  # consistent away-direction along x
            awayy = 1 if (ny - oy) * (sy - oy) > 0 else 0
            edge_pen = (nx in (0, w - 1)) + (ny in (0, h - 1))
            val = (d, awayx + awayy, -adj_obs, -(edge_pen))
        else:
            # Pursuer: prioritize minimizing distance; if tied, move in the sign that reduces both x and y when possible; penalize obstacle adjacency.
            progx = 1 if (ox - nx) * (ox - sx) > 0 else 0  # reduce gap along x
            progy = 1 if (oy - ny) * (oy - sy) > 0 else 0
            val = (-d, progx + progy, -adj_obs)

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best