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
    am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy
    def corner_bias(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dcur = dist2(sx, sy)
        dnew = dist2(nx, ny)
        if am_evader:
            # maximize distance; strongly avoid reducing distance
            val = (dnew - dcur) * 1000 + dnew
            # deterministic corner-run: prefer farther-from-center (smaller corner_bias)
            val += (7 - corner_bias(nx, ny)) * 2
        else:
            # minimize distance; prefer moves that reduce distance significantly
            val = (dnew - dcur) * 1000 - dnew
            # minor obstacle-avoidance: prefer positions with more free neighbors
            free_n = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if free(tx, ty):
                    free_n += 1
            val += free_n * 0.5
        if best is None or (val > best_val) or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]