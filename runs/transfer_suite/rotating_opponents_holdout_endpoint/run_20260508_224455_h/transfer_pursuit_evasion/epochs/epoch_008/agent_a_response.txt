def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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
    # If roles unknown, infer: if opponent is evader, we likely pursue; else assume we are evader if our role says so.
    we_evader = self_evader and not opp_evader
    if not self_evader and opp_evader:
        we_evader = False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic move ordering preference: prefer straight then diagonal, but keep fixed order.
    moves.sort(key=lambda d: (abs(d[0]) + abs(d[1]) != 1, abs(d[0]) == 1 and abs(d[1]) == 1, d[0], d[1]))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy  # engine would keep us in place; avoid obstacle reasoning
        d2 = dist2(nx, ny, ox, oy)
        # Evader: maximize distance, avoid moving into obstacle (already via blocked -> stay).
        # Pursuer: minimize distance, also avoid obstacle stalling if possible.
        if we_evader:
            val = (d2, -((nx == sx and ny == sy) and 1 or 0), -(abs(dx) + abs(dy)))
        else:
            val = (-d2, -((nx == sx and ny == sy) and 1 or 0), -(abs(dx) + abs(dy)))
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
    return [best[0], best[1]]