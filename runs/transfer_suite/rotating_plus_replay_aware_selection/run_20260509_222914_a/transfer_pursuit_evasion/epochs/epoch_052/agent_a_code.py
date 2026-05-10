def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    pref = [4, 1, 3, 5, 7, 0, 2, 6, 8]  # deterministic tie-break (center, then cardinal, then diag)
    moves = [moves[i] for i in pref]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def clamp_goal_towards(x, y, gx, gy):
        dx = 0 if gx == x else (1 if gx > x else -1)
        dy = 0 if gy == y else (1 if gy > y else -1)
        return dx, dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    goal_center = (int(round(cx)), int(round(cy)))

    def score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        d = max(abs(nx - ox), abs(ny - oy))  # chebyshev for closer capture control
        # Obstacle proximity penalty for pursuer (to keep lines open) / bonus for evader (to hide)
        obs_pen = 0
        if obstacles:
            for ax, ay in obstacles:
                md = abs(nx - ax) + abs(ny - ay)
                if md == 0:
                    return -10**9
                obs_pen += 1.0 / md
        # Evader also wants to keep away from opponent while biasing toward center lanes
        if is_pursuer:
            return (-d * 1000) - obs_pen * 3 - ((nx - sx) == 0 and (ny - sy) == 0) * 0.1
        else:
            # Prefer larger distance; add slight preference to "slip" away from opponent by moving toward farthest corner from opponent
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            tc = max(abs(nx - tx), abs(ny - ty))
            cc = max(abs(nx - goal_center[0]), abs(ny - goal_center[1]))
            return (d * 1000) + tc * 2 + cc * 0.5 - obs_pen * 1.2 - ((nx - sx) == 0 and (ny - sy) == 0) * 0.05

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = score(nx, ny)
        if best_score is None or s > best_score:
            best_score = s
            best = (dx, dy)

    if best is None:
        dx, dy = clamp_goal_towards(sx, sy, goal_center[0], goal_center[1])
        return [int(dx), int(dy)]
    return [int(best[0]), int(best[1])]