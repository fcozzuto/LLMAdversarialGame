def choose_move(observation):
    w = int(observation.get("grid_width", 1) or 1)
    h = int(observation.get("grid_height", 1) or 1)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = set(tuple(p) for p in (observation.get("resources") or []))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    targets = unclaimed or resources
    if targets:
        tlist = list(targets)
        tlist.sort(key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
        best_t = tlist[0]
        tx, ty = best_t[0], best_t[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    best = None
    best_score = -10**18
    for dx, dy in dirs + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 1000
        if (nx, ny) in resources:
            score += 200
        d_to_target = man(nx, ny, tx, ty)
        score += max(0, 200 - d_to_target)
        # Avoid giving opponent immediate advantage: prefer increasing distance from opponent
        score += min(100, man(nx, ny, ox, oy))
        # Prefer moves that reduce distance to center slightly (tie-break)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        score -= man(nx, ny, cx, cy) // 2
        # Deterministic tie-break
        tie = (score, -nx, -ny)
        if best is None or tie > best_score:
            best_score = tie
            best = [dx, dy]
    return best if best is not None else [0, 0]