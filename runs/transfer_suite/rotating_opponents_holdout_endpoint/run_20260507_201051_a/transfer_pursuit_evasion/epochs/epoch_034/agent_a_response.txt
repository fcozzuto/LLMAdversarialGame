def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def edge_margin(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    best = None
    best_move = (0, 0)
    # Deterministic tie-breaker by move order in moves list.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        blocked = (nx, ny) in obs
        if blocked:
            val = -10**18 if i_am_evader else 10**18
        else:
            d = dist2(nx, ny)
            em = edge_margin(nx, ny)
            # Evader: maximize distance; prefer center; lightly prefer keeping line-of-attack disrupted.
            if i_am_evader:
                # Encourage moving to positions that are not directly aligned with opponent when possible.
                aligned = 1 if (nx == ox or ny == oy or abs(nx - ox) == abs(ny - oy)) else 0
                val = d * 10 + em * 3 - aligned * 4 - (1 if (sx == nx and sy == ny) else 0) * 1
            # Pursuer: minimize distance; prefer moves that reduce distance most, avoid obstacles.
            else:
                aligned = 1 if (nx == ox or ny == oy or abs(nx - ox) == abs(ny - oy)) else 0
                val = -d * 10 + aligned * 2 + em * 0  # em kept small; obstacle avoidance already handled
        if best is None or (i_am_evader and val > best) or ((not i_am_evader) and val < best):
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]