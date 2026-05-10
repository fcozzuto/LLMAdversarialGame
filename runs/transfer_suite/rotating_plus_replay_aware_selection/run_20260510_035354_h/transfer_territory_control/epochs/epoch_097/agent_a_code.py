def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ax, ay, ox, oy = int(ax), int(ay), int(ox), int(oy)

    def toset(lst):
        s = set()
        if not lst:
            return s
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y, tx, ty):
        d = abs(x - tx) + abs(y - ty)
        opp = abs(x - ox) + abs(y - oy)
        return (-d) + (0.05 * opp)

    if unclaimed:
        bestt = None
        bestd = None
        bestpen = None
        for tx, ty in unclaimed:
            if (tx, ty) in obstacles:
                continue
            d = abs(tx - ax) + abs(ty - ay)
            # Prefer frontier-ish targets: those close to our current position
            pen = 0 if d <= 3 else d
            if bestd is None or (d, pen) < (bestd, bestpen):
                bestd, bestpen, bestt = d, pen, (tx, ty)
        tx, ty = bestt
        bestm = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = ax + dx, ay + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = cell_score(nx, ny, tx, ty)
            if bestv is None or v > bestv:
                bestv, bestm = v, (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # No unclaimed: move toward center while staying away from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dcen = abs(nx - cx) + abs(ny - cy)
        dopp = abs(nx - ox) + abs(ny - oy)
        v = (-dcen) + (0.08 * dopp)
        if bestv is None or v > bestv:
            bestv, bestm = v, (dx, dy)
    return [int(bestm[0]), int(bestm[1])]