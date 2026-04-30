def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Prefer moves in a deterministic order (closer to target first, then bias)
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    # Choose a target resource: pick nearest to us that opponent isn't strictly closer to (tie-break by resource order)
    best = None; best_key = None
    for p in resources:
        px, py = p
        if (px, py) in obstacles:
            continue
        ds = dist((sx, sy), (px, py))
        do = dist((ox, oy), (px, py))
        # Key: prioritize resources we can reach at least as fast; then closer to us; then deterministic by coordinates
        key = (0 if ds <= do else 1, ds, px, py)
        if best_key is None or key < best_key:
            best_key = key; best = (px, py)
    # If no resources, retreat to center-ish to avoid obstacles
    if best is None:
        tx, ty = w//2, h//2
    else:
        tx, ty = best
    # Evaluate candidate moves with obstacle + bounds; choose minimal heuristic to target and avoid giving opponent a better next step
    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            return 10**9
        # Primary: reduce distance to target
        d = dist((nx, ny), (tx, ty))
        # Secondary: avoid stepping into opponent's immediate proximity (Manhattan <=1) deterministically
        prox = 0
        if dist((nx, ny), (ox, oy)) <= 1 and (tx, ty) != (nx, ny):
            prox = 5
        return d + prox
    # Deterministic selection: scan moves in fixed order
    best_d = None; best_mv = (0, 0)
    for dx, dy in moves:
        sc = score_move(dx, dy)
        if best_d is None or sc < best_d:
            best_d = sc; best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]