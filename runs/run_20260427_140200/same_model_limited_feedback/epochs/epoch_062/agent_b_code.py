def choose_move(observation):
    W, H = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def best_target():
        if not resources:
            return None
        best = None
        best_score = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = dist2((sx, sy), (rx, ry))
            d_op = dist2((ox, oy), (rx, ry))
            score = (d_op - d_me) * 10 - d_me * 0.01
            if d_me == 0:
                score += 1e6
            best_next = (rx, ry)
            if score > best_score:
                best_score = score
                best = best_next
        return best if best is not None else resources[0]

    target = best_target()
    if target is None:
        return [0, 0]

    tx, ty = target
    # If opponent is substantially closer to all, drift to a mid-field point near nearest resource to us
    d_me_t = dist2((sx, sy), (tx, ty))
    d_op_t = dist2((ox, oy), (tx, ty))
    if d_me_t > d_op_t * 1.05 and resources:
        # choose nearest resource to self as fallback (deny less effective but stable)
        best = None
        bd = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = dist2((sx, sy), (rx, ry))
            if d < bd:
                bd = d
                best = (rx, ry)
        if best is not None:
            tx, ty = best

    # Choose move that reduces distance to target; penalize obstacles and moves that get worse.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_before = dist2((sx, sy), (tx, ty))
        d_after = dist2((nx, ny), (tx, ty))
        improve = d_before - d_after
        # Slightly prefer blocking opponent by keeping distance from them when near target
        opp_d_after = dist2((nx, ny), (ox, oy))
        val = improve * 100 - d_after * 0.5 + opp_d_after * 0.01
        # Prefer moves with minimal step distance to avoid dithering
        val -= (abs(dx) + abs(dy)) * 0.02
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]