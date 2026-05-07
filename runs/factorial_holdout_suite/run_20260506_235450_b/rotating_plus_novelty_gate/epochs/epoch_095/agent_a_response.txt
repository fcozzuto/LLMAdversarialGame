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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev for diagonal-friendly

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = r[0], r[1]
            if isinstance(tx, int) and isinstance(ty, int) and inb(tx, ty):
                rs.append((tx, ty))
    if not rs:
        return [0, 0]

    # Choose target we can reach at least as fast as the opponent; otherwise fall back to nearest.
    best = None
    best_key = None
    for tx, ty in rs:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        key = (1 if ds > do else 0, ds, do, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Move that improves our position relative to the chosen target, while staying valid.
    bestm = [0, 0]
    bestm_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds = dist(nx, ny, tx, ty)
        do = dist(ox, oy, tx, ty)
        # Prefer positions where we are not behind; otherwise maximize progress.
        key = (1 if ds > do else 0, ds, abs(nx - tx) + abs(ny - ty), nx, ny)
        if bestm_key is None or key < bestm_key:
            bestm_key = key
            bestm = [dx, dy]

    return bestm