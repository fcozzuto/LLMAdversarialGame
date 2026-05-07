def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    def diag_dist(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev: diagonal-friendly

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Prefer resources where we can arrive earlier; if none, grab the quickest available.
    best = None
    best_key = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not inside(tx, ty):
            continue
        ds = diag_dist(sx, sy, tx, ty)
        do = diag_dist(ox, oy, tx, ty)
        arrive_margin = do - ds  # positive means we are earlier
        if arrive_margin >= 1:
            key = (0, -arrive_margin, ds, -((tx + ty) & 1), -tx, -ty)
        else:
            key = (1, -do, ds, -((tx + ty) & 1), -tx, -ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    # One-step decision: move to maximize advantage at the target (and secondarily avoid being trapped by obstacles).
    bestm = [0, 0]
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nds = diag_dist(nx, ny, tx, ty)
        ndo = diag_dist(ox, oy, tx, ty)
        # Anticipate immediate advantage; prefer keeping our lead and reducing it for the opponent.
        v = (nds - ndo, nds, abs(nx - ox) + abs(ny - oy), -((nx + ny) & 1), -dx, -dy)
        if bestv is None or v < bestv:
            bestv = v
            bestm = [dx, dy]
    return [int(bestm[0]), int(bestm[1])]