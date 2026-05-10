def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                targets.append((x, y))
    if not targets:
        for c in unclaimed:
            if c and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if ok(x, y):
                    targets.append((x, y))

    cx, cy = w // 2, h // 2
    if not targets:
        targets = [(cx, cy), (ox, oy)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(a, b):
        dx, dy = a[0] - b[0], a[1] - b[1]
        return dx * dx + dy * dy

    best_dir = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 10**18
        for t in targets:
            d = dist2((nx, ny), t)
            if d < score:
                score = d
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_dir):
            best_score = score
            best_dir = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_dir[0]), int(best_dir[1])]