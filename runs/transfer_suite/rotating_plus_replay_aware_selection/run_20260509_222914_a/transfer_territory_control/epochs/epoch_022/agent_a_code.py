def choose_move(observation):
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    w = int(w) if isinstance(w, int) else int(w or 8)
    h = int(h) if isinstance(h, int) else int(h or 8)

    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obs.add((x, y))

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obs:
                targets.append((x, y))

    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obs:
                    targets.append((x, y))

    if not targets:
        targets = [(ox, oy)]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = moves[0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        here = (nx, ny)
        dt = min(dist2(here, t) for t in targets)
        do = dist2(here, (ox, oy))
        score = -dt + 0.01 * do
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best