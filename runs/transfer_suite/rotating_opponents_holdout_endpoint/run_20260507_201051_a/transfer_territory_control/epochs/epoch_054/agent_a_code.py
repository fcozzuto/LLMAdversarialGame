def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)

    raw_obs = observation.get("obstacles") or []
    try:
        obstacles = set(raw_obs)
    except TypeError:
        obstacles = set()

    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    if resources:
        try:
            targets = list(resources)
        except TypeError:
            targets = []
    if not targets and unclaimed:
        try:
            targets = list(unclaimed)
        except TypeError:
            targets = []

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue
        score = 0
        if targets:
            t = min(targets, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            score -= 4 * dist((nx, ny), t)
        score -= 1 * dist((nx, ny), (cx, cy))
        score += 1 * dist((nx, ny), (ox, oy))
        if best is None or score > best_val or (score == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = score

    return list(best) if best is not None else [0, 0]