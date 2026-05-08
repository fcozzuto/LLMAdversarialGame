def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target = None
    if resources:
        bestd = None
        for r in resources:
            if inb(r[0], r[1]) and r not in obstacles:
                d = dist2((sx, sy), r)
                if bestd is None or d < bestd:
                    bestd = d
                    target = r
    elif w and h:
        target = (ox, oy)  # fallback: posture vs opponent

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        if target is not None and resources:
            v += -dist2((nx, ny), target) * 10  # chase nearest resource
        # keep some distance from opponent, but don't freeze
        v += dist2((nx, ny), (ox, oy)) * 2

        # deterministic nudge toward the board center to avoid loops in empty maps
        if w and h:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            v += -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.01

        if v > best_val:
            best_val = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best