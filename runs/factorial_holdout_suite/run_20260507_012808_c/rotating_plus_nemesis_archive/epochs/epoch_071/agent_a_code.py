def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # Head toward center when no visible resources
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles:
            # Try axis move
            if (sx + dx, sy) not in obstacles:
                dy = 0
            elif (sx, sy + dy) not in obstacles:
                dx = 0
            else:
                dx = 0
                dy = 0
        return [dx, dy]

    # Pick a target resource with bias to race advantage
    # Smaller score is better: self_dist - 0.6*opp_dist
    best_r = None
    best_s = None
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        s = sd - 0.6 * od
        if best_s is None or s < best_s:
            best_s = s
            best_r = r

    tx, ty = best_r
    options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            blocked = (nx, ny) in obstacles
            nsd = dist((nx, ny), best_r)
            nod = dist((ox, oy), best_r)
            # Prefer moves that reduce own distance, and (slightly) increase opponent gap
            score = 1000 * (1 if blocked else 0) + nsd - 0.2 * (nod - nsd)
            # Deterministic tie-break: fewer diagonal steps, then lexicographic dx,dy
            diag = 1 if (dx != 0 and dy != 0) else 0
            options.append((score, diag, dx, dy))
    options.sort()
    _, _, dx, dy = options[0]
    return [int(dx), int(dy)]