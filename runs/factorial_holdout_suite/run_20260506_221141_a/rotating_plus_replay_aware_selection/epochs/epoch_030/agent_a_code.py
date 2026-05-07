def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def cell_score(nx, ny):
        if not resources:
            # Drift toward center while avoiding obstacles.
            cx, cy = (gw - 1) // 2, (gh - 1) // 2
            return -cheb(nx, ny, cx, cy), 0, nx, ny
        best_adv = -10**18
        best_dself = 10**9
        best_cell = resources[0]
        for rx, ry in resources:
            dself = cheb(nx, ny, rx, ry)
            dopp = cheb(ox, oy, rx, ry)
            # Encourage resources we can reach before (or at parity with) opponent.
            adv = (dopp - dself)
            # Extra push if we are strictly closer than opponent (more likely to secure).
            if dself <= dopp:
                adv += 0.5
            # If multiple similar, prefer nearer to our position.
            if adv > best_adv or (adv == best_adv and dself < best_dself) or (adv == best_adv and dself == best_dself and (rx, ry) < best_cell):
                best_adv = adv
                best_dself = dself
                best_cell = (rx, ry)
        return best_adv, best_dself, best_cell[0], best_cell[1]

    # If no resources, just move to reduce distance to center.
    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = (10**18, 0, 0, 0)
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            cand = (d, abs(dx) + abs(dy), nx, ny)
            if cand < best:
                best = cand
                best_move = [dx, dy]
        return best_move

    best = (-10**18, 10**9, 0, 0)
    best_move = [0, 0]
    # Deterministic tie-break order: moves list order already fixed.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        adv, dself, tx, ty = cell_score(nx, ny)
        # Stronger preference for higher advantage; then closer to target; then lexicographic stability.
        cand = (adv, -dself, -tx, -ty)
        if cand > best:
            best = cand
            best_move = [dx, dy]
    return best_move