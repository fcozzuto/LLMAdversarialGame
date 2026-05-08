def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    # If no visible resources, move toward center-right bias to change policy
    if not resources:
        tx, ty = (w - 2 if sx < w // 2 else w - 1), (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            return [0, 0]
        return [dx if 0 <= nx < w else 0, dy if 0 <= ny < h else 0]

    # Score candidate by taking the best "winning margin" to any reachable resource,
    # then slightly prefer larger margins against opponent and closeness to self.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        best_margin = -10**9
        best_self_d = 10**9
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            margin = od - sd  # positive means we arrive sooner (or already on it)
            if margin > best_margin or (margin == best_margin and sd < best_self_d):
                best_margin = margin
                best_self_d = sd

        # Secondary: reduce opponent chance by moving away if margin is poor.
        opp_close = md(nx, ny, ox, oy)
        score = best_margin * 1000 - best_self_d - opp_close * (1 if best_margin < 0 else 0)

        # Tertiary deterministic tie-break: prefer moves with smaller dx, then smaller dy.
        tie = (score == best_score)
        if best is None or score > best_score or (tie and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]