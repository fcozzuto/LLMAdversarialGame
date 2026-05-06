def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Deterministic target selection: closest resource to us; tie by (x,y)
    best_r = None
    best_key = None
    for rx, ry in resources:
        k = (man(sx, sy, rx, ry), ry, rx)
        if best_key is None or k < best_key:
            best_key = k
            best_r = (rx, ry)
    tx, ty = best_r

    # Resource centroid as secondary long-term anchor
    cx = sum(p[0] for p in resources) / len(resources)
    cy = sum(p[1] for p in resources) / len(resources)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    cur_my_to_t = man(sx, sy, tx, ty)
    cur_my_to_cent = man(sx, sy, cx, cy)
    cur_opp_to_t = man(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_t = man(nx, ny, tx, ty)
        opp_t = man(ox, oy, tx, ty)
        my_cent = man(nx, ny, cx, cy)

        # Primary: win-the-race on the current target resource
        # Large positive when we reduce our distance relative to opponent.
        score = (opp_t - my_t) * 10

        # Secondary: actually move toward target and centroid (stable long-term)
        score += (cur_my_to_t - my_t) * 5
        score += (cur_my_to_cent - my_cent) * 2

        # Tertiary: reduce distance to all resources modestly (avoid dead-ends)
        # Use min and average of nearest few (deterministic via full scan).
        ds = [man(nx, ny, rx, ry) for rx, ry in resources]
        ds_sorted = sorted(ds)
        score += (ds_sorted[0] * -1) * 1.5
        score += (sum(ds_sorted[:3]) / 3.0) * -0.7

        # Anti-stall: staying still only allowed if it doesn't lose target race
        if dx == 0 and dy == 0:
            score -= 3.0
            if my_t > cur_my_to_t:
                score -= 50.0

        # Additional safety: prefer moving that increases opponent distance to target
        score += (man(ox, oy, tx, ty) - man(ox, oy, tx, ty)) * 0  # deterministic no-op

        # Deterministic tie-breaker by dx,dy order
        key = (score, -abs(dx) - abs(dy), -dx, -dy)
        if key > (best_score, -abs(best_move[0]) - abs(best_move[1]), -best_move[0], -best_move[1]):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]