def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources visible, drift to farthest corner from opponent
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = None
        for cx, cy in corners:
            if not inb(cx, cy):
                continue
            v = (dist((ox, oy), (cx, cy)), -dist((sx, sy), (cx, cy)))
            if bestv is None or v > bestv:
                bestv = v
                best = (cx, cy)
        if best is None:
            return [0, 0]
        tx, ty = best
    else:
        # Prefer resources where we are closer than opponent; also break ties by being nearer.
        best = None
        bestv = None
        for r in resources:
            sd = dist((sx, sy), r)
            od = dist((ox, oy), r)
            # Strong bias: take advantage of being closer; mild bias to reduce own distance.
            adv = od - sd
            tie = -sd
            # Slightly discourage targets very near opponent (likely denial attempts).
            risk = -min(od, 6)
            v = (adv, tie, risk)
            if bestv is None or v > bestv:
                bestv = v
                best = r
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    if dx != 0 and dy != 0:
        candidates = [(dx, dy), (dx, 0), (0, dy)]
    else:
        candidates = [(dx, dy), (dx, 0), (0, dy)]
    # Ensure deterministic fallback order
    candidates += [(dx if dx != 0 else 0, dy if dy != 0 else 0), (-dx, dy), (dx, -dy), (0, 0)]

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny):
            return [mx, my]
    return [0, 0]