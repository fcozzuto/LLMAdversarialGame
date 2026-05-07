def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        dx = abs(a - b)
        dy = abs(c - d)
        return dx if dx > dy else dy  # Chebyshev for diagonal speed

    # Choose a resource that we can reach relatively sooner than the opponent (deny priority).
    best_t = None
    best_k = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
            continue
        ds = dist(sx, tx, sy, ty)
        do = dist(ox, tx, oy, ty)
        # Larger is better: deny window first, then prefer closer.
        k = (do - ds, -ds, -((tx + ty) & 1), tx, ty)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # One-step greedy: pick move maximizing immediate target progress and deny advantage.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_new = dist(nx, tx, ny, ty)
        do_cur = dist(ox, tx, oy, ty)
        # prefer reaching/collecting sooner; also slightly prefer moving away from opponent's direct advantage
        score = (do_cur - ds_new, -ds_new, -(abs(nx - ox) + abs(ny - oy)), nx, ny, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]