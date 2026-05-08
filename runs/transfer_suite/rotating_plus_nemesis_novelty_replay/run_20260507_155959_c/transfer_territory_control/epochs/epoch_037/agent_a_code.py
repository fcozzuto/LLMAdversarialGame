def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells", []) or []
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        # higher is better
        # prefer capturing near center, avoid obstacles (penalize), prefer opponent for flip
        near_center = -(abs(x - cx) + abs(y - cy))
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in opp_cells:
            return near_center + 5.0  # flipping on entry enabled
        if (x, y) in self_cells:
            return near_center - 1.0  # don't waste time re-entering own already-held cells
        return near_center + 1.0

    target = None
    bestt = None
    for x, y in unclaimed:
        x, y = int(x), int(y)
        if not inb(x, y) or (x, y) in obstacles:
            continue
        sc = score_cell(x, y)
        if bestt is None or sc > bestt or (sc == bestt and (y, x) < (best[1], best[0])):
            bestt = sc
            best = (x, y)
    if bestt is None:
        best = (sx, sy)

    tx, ty = best[0], best[1]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moves that go closer to target; tie-break with center/control priorities
        dist = abs(nx - tx) + abs(ny - ty)
        v = -dist * 10 + score_cell(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]