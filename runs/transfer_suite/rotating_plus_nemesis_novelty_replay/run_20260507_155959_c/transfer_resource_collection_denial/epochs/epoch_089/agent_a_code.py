def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx == 0 and dy == 0) or (inb(nx, ny) and (nx, ny) not in obs):
                if dx == 0 and dy == 0:
                    moves.append((0, 0))
                else:
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = abs(nx - cx) + abs(ny - cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def dist(a, b, x, y):
        return abs(a - x) + abs(b - y)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    bestm, bestscore = (0, 0), None

    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy

        # Find the resource we can contest best (maximize opp-self distance gap).
        best_gap = None
        best_self = None
        for rx, ry in resources:
            myd = dist(nsx, nsy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            gap = opd - myd
            if best_gap is None or gap > best_gap or (gap == best_gap and myd < best_self):
                best_gap, best_self = gap, myd

        # If we're not ahead on any resource, move to reduce our time and also
        # drift to center to reduce future denier advantage.
        center_pen = 0.25 * (abs(nsx - cx) + abs(nsy - cy))
        score = (best_gap if best_gap is not None else -10**9) - 0.5 * (best_self if best_self is not None else 10**9) - center_pen

        if bestscore is None or score > bestscore:
            bestscore = score
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]