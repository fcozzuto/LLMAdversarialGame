def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Pick best resource to reach earlier than opponent (tie-break: shorter our distance)
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)  # prefer we are closer (ds-do), then we are close
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    curr_ds = cheb(sx, sy, tx, ty)
    # Evaluate each legal move; deterministic tie-break by dir order
    best_step = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)

        # Small heuristic: improve our distance to target strongly;
        # penalize giving opponent a better position indirectly by aiming to reduce
        # the chance they are closer to more resources.
        score = 0
        score += (curr_ds - nds) * 100

        # If we get closer while opponent is also closer, still okay; but prioritize contesting
        # resources that opponent is already as close or closer to.
        if nds == 0:
            score += 5000
        opp_closer = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dself = cheb(nx, ny, rx, ry)
            dold = cheb(ox, oy, rx, ry)
            if dold <= dself:
                opp_closer += 1
        score -= opp_closer * 3

        # Also prefer moves that don't increase distance to target too much (already handled), and
        # slightly prefer diagonal progress toward target when equal.
        score -= (abs(nx - tx) + abs(ny - ty)) * 0.01

        if best_score is None or score > best_score:
            best_score = score
            best_step = [dx, dy]

    return best_step