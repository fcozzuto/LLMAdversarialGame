def choose_move(observation):
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    gw, gh = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    ox, oy = observation["opponent_position"]

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -(cheb(nx, ny, tx, ty))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Deterministically pick the resource with best relative approach.
    best_r = None
    best_key = (-10**18, 10**18)  # (lead, mydist)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        lead = oppd - myd  # positive means we're closer
        key = (lead, myd)
        if key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # Among legal moves, greedily reduce distance to target; break ties by increasing lead.
    chosen = [0, 0]
    chosen_key = (-10**18, -10**18, 10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd2 = cheb(nx, ny, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        lead2 = oppd - myd2
        # Prefer: higher lead, then lower my distance, then deterministic delta ordering from moves list.
        key = (lead2, -myd2, abs(dx) + abs(dy))
        if key > chosen_key:
            chosen_key = key
            chosen = [dx, dy]

    return chosen