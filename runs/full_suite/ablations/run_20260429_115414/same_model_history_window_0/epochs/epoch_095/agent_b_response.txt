def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # No resources: retreat toward center-ish to avoid deadlocks, still deterministic
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)
    else:
        best = None
        bestv = None
        for r in resources:
            md = dist((sx, sy), r)
            od = dist((ox, oy), r)
            # Prefer resources I'm at least as close to; break ties by smaller my distance
            v = (md - od * 0.9, md, r[0], r[1])
            if bestv is None or v < bestv:
                bestv = v
                best = r
        target = best

    tx, ty = target
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Heuristic: minimize distance to target, keep away from opponent if close, prefer not to worsen
        nd = dist((nx, ny), (tx, ty))
        od = dist((nx, ny), (ox, oy))
        curd = dist((sx, sy), (tx, ty))
        curod = dist((sx, sy), (ox, oy))
        score = (nd, -od, 0 if nd <= curd else 1, -od + curod * 0.0, dx, dy)
        candidates.append((score, (dx, dy)))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0])
    return list(candidates[0][1])