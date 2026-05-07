def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach earlier; tie-break by closer to us.
            score = (opd - myd, -myd)
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        # Secondary: avoid moving into opponent-proximal squares (resource denier)
        opd = dist((nx, ny), (ox, oy))
        candidates.append(((myd, -opd), (dx, dy)))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0][0], t[0][1]))
    return [candidates[0][1][0], candidates[0][1][1]]