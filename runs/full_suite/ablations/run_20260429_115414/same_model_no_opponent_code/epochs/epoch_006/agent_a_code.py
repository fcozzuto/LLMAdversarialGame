def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand_moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    res = [(int(x), int(y)) for x, y in resources]
    if not res:
        res = [(w // 2, h // 2)]

    # Target choice: prefer resources where we are closer than opponent, but also keep some progress.
    best_t = None
    best_k = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        k = (-(do - ds), ds, rx, ry)  # minimize opponent advantage gap; then nearest
        if best_k is None or k < best_k:
            best_k = k
            best_t = (rx, ry)
    tx, ty = best_t

    best_move = (0, 0)
    best_val = None
    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate move by how much it improves our access to resources and denies opponent.
        # Also include small penalty for getting too close to opponent (reduce collision/contests).
        my_near = 10**9
        op_near = 10**9
        for rx, ry in res:
            my_near = min(my_near, cheb(nx, ny, rx, ry))
            op_near = min(op_near, cheb(ox, oy, rx, ry))
        to_target = cheb(nx, ny, tx, ty)
        opp_to_target = cheb(ox, oy, tx, ty)
        gap = (opp_to_target - to_target)  # higher means we are relatively closer to target
        # Deterministic tie-break uses coordinates.
        val = (-(gap * 100) + my_near * 3 - op_near * 2) + (abs(nx - sx) + abs(ny - sy)) * 0.01
        t = (val, to_target, nx, ny)
        if best_val is None or t < best_val:
            best_val = t
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]