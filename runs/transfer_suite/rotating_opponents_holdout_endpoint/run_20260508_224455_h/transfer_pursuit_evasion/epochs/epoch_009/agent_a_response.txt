def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_evader = any(k in role for k in ("evader", "evade", "escape", "runner"))
    opp_evader = any(k in opp_role for k in ("evader", "evade", "escape", "runner"))
    we_evader = self_evader and not opp_evader
    if (not self_evader) and opp_evader:
        we_evader = False  # likely pursuer

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda d: (d[0] == 0 and d[1] == 0, abs(d[0]) + abs(d[1]) == 2, abs(d[0]), abs(d[1]), d[0], d[1]))

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not blocked(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    best = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        d = dist2(nx, ny, ox, oy)
        # One-step obstacle/bounds penalty to reduce "dodgy" moves (deterministic).
        extra = 0
        if not inb(nx, ny): extra += 1000
        if blocked(nx, ny): extra += 1000
        # Additional tie-break: prefer moving generally toward/away from opponent.
        toward = (nx - sx, ny - sy)
        bias = abs(toward[0]) + abs(toward[1])

        val = (d + extra, bias)
        if best is None:
            best, best_val = (dx, dy), val
        else:
            if we_evader:
                # maximize distance => minimize negative
                if val[0] > best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]):
                    best, best_val = (dx, dy), val
            else:
                # minimize distance
                if val[0] < best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]):
                    best, best_val = (dx, dy), val

    return [int(best[0]), int(best[1])]