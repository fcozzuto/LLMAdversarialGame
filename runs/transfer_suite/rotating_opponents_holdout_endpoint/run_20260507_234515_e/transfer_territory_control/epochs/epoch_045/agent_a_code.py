def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0] if len(sp) > 0 else 0), int(sp[1] if len(sp) > 1 else 0)
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0] if len(op) > 0 else w - 1), int(op[1] if len(op) > 1 else h - 1)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))
    if not targets:
        unclaimed = observation.get("unclaimed_cells") or []
        for p in unclaimed:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if targets:
            d = min(man((nx, ny), t) for t in targets)
            score += 1000 - d
        score += 20 * (man((nx, ny), (ox, oy)) * -1)  # prefer being farther from opponent
        score += 1 if (nx, ny) == (ox, oy) else 0
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]