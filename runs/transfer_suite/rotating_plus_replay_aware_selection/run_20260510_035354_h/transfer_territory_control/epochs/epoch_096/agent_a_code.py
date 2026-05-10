def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def norm(p):
        try:
            return int(p[0]), int(p[1])
        except Exception:
            return 0, 0

    ax, ay = norm((ax, ay))
    ox, oy = norm((ox, oy))

    obstacles = observation.get("obstacles") or []
    def toset(lst):
        s = set()
        for p in lst:
            try:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
            except Exception:
                pass
        return s

    obs = toset(obstacles)
    unclaimed = observation.get("unclaimed_cells") or []
    u = toset(unclaimed)

    self_terr = observation.get("self_territory") or []
    self_t = toset(self_terr)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Target: nearest unclaimed; if none, bias toward expanding from our territory toward center.
    if u:
        # Use a deterministic nearest by Manhattan distance; break ties by lexicographic.
        target = None
        bestd = None
        for x, y in u:
            d = abs(x - ax) + abs(y - ay)
            if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                bestd = d
                target = (x, y)
    else:
        # Pick a deterministic neighbor cell around our territory (or center if none).
        if self_t:
            tx, ty = None, None
            bestd = None
            for x, y in self_t:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if inb(nx, ny) and (nx, ny) not in self_t and (nx, ny) not in obs:
                            d = abs(nx - cx) + abs(ny - cy)
                            if bestd is None or d < bestd or (d == bestd and (nx, ny) < (tx, ty)):
                                bestd = d
                                tx, ty = nx, ny
            target = (tx, ty) if tx is not None else (cx, cy)
        else:
            target = (cx, cy)

    # Score each legal move by closeness to target; discourage obstacles; slight push away from opponent.
    best = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dt = abs(target[0] - nx) + abs(target[1] - ny)
        do = abs(ox - nx) + abs(oy - ny)
        score = (-dt) + (0.05 * do)
        if bestscore is None or score > bestscore or (score == bestscore and (dx, dy) < best):
            bestscore = score
            best = (dx, dy)

    if best is None:
        # Fallback: stay if possible
        if inb(ax, ay) and (ax, ay) not in obs:
            return [0, 0]
        for dx, dy in moves:
            nx, ny = ax + dx, ay + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
    return [best[0], best[1]] if best is not None else [0, 0]