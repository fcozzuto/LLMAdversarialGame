def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "evader" in opp_role)
    if ("evader" in self_role) and ("pursuer" in opp_role):
        pursuer = False

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    best_dxdy = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = dist_manh(nx, ny, ox, oy)

        # obstacle penalty: prefer not to be adjacent to obstacles (helps against wall runners)
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj += 1

        # "escape corridor" heuristic for evader: keep moving in the direction that reduces the number
        # of blocked neighbors while increasing distance; for pursuer invert it.
        blocked_moves = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if not ok(tx, ty):
                blocked_moves += 1

        if pursuer:
            score = (d * -1.0) + (adj * -0.15) + (blocked_moves * -0.02)  # minimize distance, avoid dead ends
        else:
            score = (d * 1.0) + (adj * -0.2) + (blocked_moves * -0.05)     # maximize distance, avoid getting boxed in

        # Small deterministic tie-break: prefer diagonal/axis toward opponent's line for pursuer, away for evader
        if best_score is None or score > best_score + 1e-12:
            best_score = score
            best_dxdy = (dx, dy)
        elif abs(score - best_score) <= 1e-12:
            # deterministic secondary: lexicographic on (abs(dx)+abs(dy), dx, dy) with desired direction
            def key(v):
                kdx, kdy = v
                primary = abs(kdx) + abs(kdy)
                if pursuer:
                    align = -dist_manh(sx + kdx, sy + kdy, ox, oy)
                else:
                    align = dist_manh(sx + kdx, sy + kdy, ox, oy)
                return (-primary, -align, kdx, kdy)
            if key((dx, dy)) < key(best_dxdy):
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]