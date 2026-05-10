def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    targets = res[:]
    if not targets:
        # Prefer expanding into nearby unclaimed territory (deterministic)
        candidates = [c for c in unclaimed if c not in my_terr and c not in obstacles]
        if candidates:
            candidates.sort(key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
            targets = candidates[:8]

    if not targets:
        # Fallback: chase opponent (or stay)
        targets = [(ox, oy)]

    target = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(target[0] - nx) + abs(target[1] - ny)
        key = (d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]