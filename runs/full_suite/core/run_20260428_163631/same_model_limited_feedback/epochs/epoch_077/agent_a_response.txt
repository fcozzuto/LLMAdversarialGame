def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources, move to center-ish deterministically
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inside(nx, ny) or (nx, ny) in obstacles:
                    continue
                v = -(abs(nx - tx) + abs(ny - ty))
                if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                    bestv = v
                    best = [dx, dy]
        return best

    # Choose resource where we are relatively more advantageous
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        adv = do - ds  # higher means we are closer than opponent
        key = (adv, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)
    rx, ry = best_res

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                deltas.append((0, 0))
            else:
                deltas.append((dx, dy))
    # Deterministic tie-break: prefer smallest dx then dy among equal scores
    best = (0, 0)
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target; Secondary: keep away from obstacles by slight penalty near them; Tertiary: avoid giving opponent advantage
        d_self = dist((nx, ny), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        # If we can get closer than opponent, prefer it
        score = (d_opp - d_self) * 1000 - d_self
        # Minor obstacle proximity penalty
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    prox += 1
        score -= prox
        # Mild discouragement of moving away from target
        if d_self > dist((sx, sy), (rx, ry)):
            score -= 5
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]