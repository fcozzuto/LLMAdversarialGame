def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    targets = []
    for k in ("unclaimed_cells", "resources"):
        v = observation.get(k)
        if v:
            for p in v:
                if p and len(p) >= 2:
                    targets.append((int(p[0]), int(p[1])))
            if targets:
                break

    dirs = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
    best = None
    best_move = [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if targets:
            d = min(mdist((nx, ny), t) for t in targets)
            score = -d
        else:
            score = -mdist((nx, ny), (ox, oy))
        score += 0.01 * mdist((nx, ny), (ox, oy))  # slight preference to keep distance
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move if best is not None else [0, 0]