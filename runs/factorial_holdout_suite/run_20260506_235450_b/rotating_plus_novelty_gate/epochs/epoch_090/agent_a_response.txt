def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    candidates = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                ds = dist(sx, sy, x, y)
                do = dist(ox, oy, x, y)
                # Advantage: higher means we are closer (or opp farther). Small tie-break on coordinate.
                advantage = (do - ds) * 1000 - ds
                candidates.append((advantage, x, y, ds, do))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, tx, ty, _, _ = candidates[0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = dist(nx, ny, tx, ty)
        # Prefer moves that also keep us not too close to opponent (reduce risk of being out-raced behind obstacles).
        d2 = dist(nx, ny, ox, oy)
        key = (d1, -d2, dx, dy)
        if key < best:
            best = key

    return [best[2], best[3]]