def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", (0, 0))
    opp = observation.get("opponent_position", (ax, ay))
    oppx, oppy = opp[0], opp[1]

    def toset(x):
        s = set()
        if not x:
            return s
        for p in x:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    uset = toset(observation.get("self_territory"))

    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_step(tx, ty):
        best = None
        bestd = None
        for dx, dy in adj4 + [(0, 0)]:
            nx, ny = ax + dx, ay + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (oppx, oppy):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if uset and (nx, ny) in uset:
                d -= 0.001
            if best is None or d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - ax) + abs(p[1] - ay), p[0], p[1]))
        return best_step(tx, ty)

    # No unclaimed: go toward opponent if safe, else toward center.
    target = (oppx, oppy)
    if not obstacles or not inb(target[0], target[1]) or target in obstacles:
        target = (w // 2, h // 2)
    return best_step(target[0], target[1])