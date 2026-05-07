def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_target(t):
        ds = abs(t[0] - sx) + abs(t[1] - sy)
        do = abs(t[0] - ox) + abs(t[1] - oy)
        # Prefer closer to self; penalize being closer to opponent (likely loss of race)
        return ds - 0.85 * do + 0.02 * (abs(t[0] - (w - 1)) + abs(t[1] - (h - 1)))

    # If no visible resources, drift toward safer corner opposite opponent
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy) + 0.01 * dist(c, (ox, oy)))
        resources = [(tx, ty)]

    target = min(resources, key=score_target)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            ns = abs(nx - target[0]) + abs(ny - target[1])
            no = abs(nx - ox) + abs(ny - oy)
            # prefer reducing distance to target and, secondarily, increase distance from opponent
            val = ns - 0.15 * no
            if best is None or val < best[0] or (val == best[0] and (nx, ny) < best[1]):
                best = (val, nx, ny)

    if best is None:
        return [0, 0]
    return [best[1] - sx, best[2] - sy]