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
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    # For evader: choose a target corner/farthest direction, then move greedily with obstacle penalty.
    if i_am_evader:
        # Deterministic target: farthest from pursuer among corners; if tie, prefer corner farthest from self.
        best_corner = corners[0]
        best_cd = -1
        for c in corners:
            cd = dist2(c[0], c[1])
            if cd > best_cd or (cd == best_cd and (dist2(sx, sy) - dist2(c[0], c[1])) > 0):
                best_cd = cd
                best_corner = c

        tx, ty = best_corner
        best = (-10**30, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                nx, ny = sx, sy
            if (nx, ny) in obs:
                continue
            # Primary: maximize distance from opponent.
            d = dist2(nx, ny)
            # Secondary: progress away from opponent towards the chosen corner.
            prog = -((abs(tx - nx) + abs(ty - ny)) * 0.5)
            # Tertiary: prefer staying near edges when blocked (escape latitude).
            edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
            score = d * 10.0 + prog + edge * 0.01
            if score > best[0]:
                best = (score, (dx, dy))
        return list(best[1] if best[1] is not None else (0, 0))
    else:
        # For pursuer: move greedily toward evader, prefer moves that reduce distance most; avoid obstacles.
        # Tie-breaker: prefer direction that also reduces Manhattan to opponent.
        best = (10**30, None)
        best_manh = 10**30
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                nx, ny = sx, sy
            if (nx, ny) in obs:
                continue
            d = dist2(nx, ny)
            m = abs(ox - nx) + abs(oy - ny)
            # Slightly prefer moves that keep more options (not too close to boundary).
            edge_pen = min(nx, ny, w - 1 - nx, h - 1 - ny)
            # Lower is better for (d, m), and higher edge_pen is slightly better.
            key = (d, m, -edge_pen * 0.01)
            if key < (best[0], best_manh, -1e9):
                best = (d, (dx, dy))
                best_manh = m
        return list(best[1] if best[1] is not None else (0, 0))