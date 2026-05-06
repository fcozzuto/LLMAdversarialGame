def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def kd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: kd(m[2], m[3], tx, ty) + 0.2 * kd(m[2], m[3], ox, oy))
        return [best[0], best[1]]

    # Choose a target to either grab (self-leaning) or block (opponent-leaning)
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = kd(sx, sy, rx, ry)
        do = kd(ox, oy, rx, ry)
        # Prefer resources we're closer to; but also strongly consider ones opponent is closer to.
        # key: higher "need" should be prioritized, so use negative in min
        need = (do - ds)  # positive => we're closer
        contest = do - ds
        # If opponent is much closer, prioritize blocking/intercepting.
        key = (0, ds) if contest >= 0 else (1, -contest)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # Evaluate moves with an intercept-aware score
    best_move = (0, 0, 0, 0)
    best_val = None
    for dx, dy, nx, ny in valid:
        myd = kd(nx, ny, tx, ty)
        oppd = kd(nx, ny, ox, oy)

        # Intercept bonus: if opponent is close to the same target, step toward it even if not closest.
        opp_target_d = kd(ox, oy, tx, ty)
        intercept = 0.0
        if opp_target_d <= 2:
            intercept = 2.2 / (1 + myd)

        # Safety/avoidance for edge patrol: avoid moving into very near cells to opponent
        avoid = 0.0
        if oppd <= 1:
            avoid = 3.0
        elif oppd <= 2:
            avoid = 1.2

        # Minor resource-steering: prefer reducing distance to some resource, not only target
        nearest = 10**9
        for rx, ry in resources:
            d = kd(nx, ny, rx, ry)
            if d < nearest:
                nearest = d
        steer = 0.35 * nearest

        val = -2.3 * (myd) + intercept - avoid + steer
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]