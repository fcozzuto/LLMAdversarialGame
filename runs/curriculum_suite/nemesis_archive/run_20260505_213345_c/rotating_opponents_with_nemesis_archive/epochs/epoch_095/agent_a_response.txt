def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_present = observation.get("opponent_position") is not None
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Choose a target resource with a bias for resources where we're not worse than the opponent.
    candidates = []
    for r in resources:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r) if opp_present else 999
        candidates.append((r, ds, do))
    candidates.sort(key=lambda t: (t[1] - 0.35 * t[2], t[0][0], t[0][1]))
    target = candidates[0][0]

    # Evaluate 1-step move by progress to target and safety vs opponent proximity.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = dist((nx, ny), target)
        # Prefer moves that reduce distance to target more than opponent gets closer.
        nos = dist((nx, ny), (ox, oy))
        # If opponent is very close, avoid moving adjacent unless it improves target distance.
        adj_pen = 0
        if nos <= 1:
            adj_pen = 0.6 if ns >= dist((sx, sy), target) else 0.0

        # Slight tie-breaker: move toward center-ish to avoid getting stuck on edges.
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center = abs(nx - cx) + abs(ny - cy)
        base = -ns - 0.12 * center - adj_pen

        if best_val is None or base > best_val or (base == best_val and (dxm, dym) < best_move):
            best_val = base
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]