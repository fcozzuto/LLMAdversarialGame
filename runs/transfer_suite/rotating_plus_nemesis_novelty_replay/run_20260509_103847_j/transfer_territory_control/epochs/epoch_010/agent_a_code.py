def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    cx, cy = w // 2, h // 2

    oppT = observation.get("opponent_territory") or []
    unT = observation.get("unclaimed_cells") or []

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target: opponent-controlled cell closest to center (to contest their "center claim")
    target = None
    if oppT:
        best = None
        for x, y in oppT:
            x, y = int(x), int(y)
            sc = dist(cx, cy, x, y) * 3 + dist(sx, sy, x, y)
            if best is None or sc < best:
                best = sc
                target = (x, y)
    if target is None and unT:
        best = None
        for x, y in unT:
            x, y = int(x), int(y)
            sc = dist(cx, cy, x, y) * 3 + dist(sx, sy, x, y)
            if best is None or sc < best:
                best = sc
                target = (x, y)
    if target is None:
        target = (cx, cy)

    # Choose among legal deltas by minimizing distance to target while staying away from obstacles/opponent
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    oxT = set((int(x), int(y)) for x, y in oppT)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_to_target = dist(nx, ny, target[0], target[1])
        # Prefer stepping into opponent territory (flipping on entry)
        flip_bonus = -8 if (nx, ny) in oxT else 0
        # Avoid getting too close to opponent (so we don't run into their next claim wave)
        opp_proximity_pen = 0
        dd = dist(nx, ny, ox, oy)
        if dd <= 2:
            opp_proximity_pen = (3 - dd) * 2

        # Mild preference to expand in the same direction (deterministic tie-breaker)
        dir_align = -(dx * (target[0] - sx) + dy * (target[1] - sy))

        score = d_to_target * 3 + opp_proximity_pen + dir_align + flip_bonus
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]