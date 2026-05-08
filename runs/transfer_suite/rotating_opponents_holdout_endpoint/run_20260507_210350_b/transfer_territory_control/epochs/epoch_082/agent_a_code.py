def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = set(map(tuple, observation.get("self_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    bestv = -10**18
    for x, y in unclaimed:
        if not inb(x, y) or (x, y) in obstacles:
            continue
        sd = md(x, y, sx, sy)
        od = md(x, y, ox, oy)
        dc = md(x, y, int(cx), int(cy))
        v = (od - sd) * 8 - dc * 2 + (2 if (x, y) not in self_terr else -1)
        if v > bestv:
            bestv = v
            best = (x, y)

    if best is None:
        best = (ox, oy)

    tx, ty = best
    bestm = [0, 0]
    bestmv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer reducing distance to target; break ties by staying safe/central.
        mv = -md(nx, ny, tx, ty) * 10 - md(nx, ny, int(cx), int(cy)) * 0.5 + (1 if (nx, ny) == (sx, sy) else 0)
        if mv > bestmv:
            bestmv = mv
            bestm = [dx, dy]
    return bestm