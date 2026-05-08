def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    if not unclaimed:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    edges = []
    for x, y in unclaimed:
        if x == 0 or y == 0 or x == w - 1 or y == h - 1:
            edges.append((x, y))
    targets = edges if edges else list(unclaimed)

    def mindist(p):
        x, y = p
        best = 10**9
        for tx, ty in targets:
            d = abs(x - tx) + abs(y - ty)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 2
        elif (nx, ny) in oppT:
            gain += 1
        elif (nx, ny) in selfT:
            gain += 0

        d1 = mindist((nx, ny))
        d2 = mindist((ox, oy))  # current opponent pressure proxy
        oppd = abs(nx - ox) + abs(ny - oy)
        center_bias = -(abs(nx - cx) + abs(ny - cy)) * 0.02

        v = gain * 10.0 - d1 * 0.25 + oppd * 0.03 + (d2 - d1) * 0.05 + center_bias
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]