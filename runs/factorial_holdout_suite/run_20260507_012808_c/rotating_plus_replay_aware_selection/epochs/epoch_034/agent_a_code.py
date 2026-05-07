def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def clamp(dx, dy):
        nx, ny = sx + dx, sy + dy
        if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
            return [0, 0]
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return [0, 0]
        return [dx, dy]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = 0, 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return clamp(dx, dy)

    def obst_pen(x, y):
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    p += 1
        return p

    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        # Prefer resources where we beat the opponent, but keep near-term progress
        # Higher is better: big advantage + slight preference for closer.
        adv = d_op - d_me
        score = adv * 10 - d_me - 2 * (obst_pen(rx, ry) + 0)
        if score > best_score or (score == best_score and (rx, ry) < best_r):
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    # Choose among up to 9 moves deterministically by local improvement toward target.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    moves.sort(key=lambda m: (m[0], m[1]))
    best_m = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        cand = clamp(dx, dy)
        cx, cy = sx + cand[0], sy + cand[1]
        if (cx, cy) == (sx, sy) and (dx, dy) != (0, 0):
            continue
        d_new = man(cx, cy, tx, ty)
        d_old = man(sx, sy, tx, ty)
        # If it blocks us (stay), penalize; otherwise maximize reduction and avoid obstacle adjacency.
        val = (d_old - d_new) * 100 - d_new - 5 * obst_pen(cx, cy)
        # Add slight preference to prevent opponent interference by moving closer to same target.
        d_op_new = man(ox, oy, tx, ty)
        val += 0.2 * (d_op_new - d_new)
        if val > best_val:
            best_val = val
            best_m = (dx, dy)

    return clamp(best_m[0], best_m[1])