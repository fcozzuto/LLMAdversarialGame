def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    if not resources:
        # Fallback: drift toward center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                val = -cheb(nx, ny, tx, ty)
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
        return best_move

    res_list = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res_list.append((rx, ry))
    if not res_list:
        return [0, 0]

    res_set = set(res_list)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # Evaluate best resource we can contest after this move
        my_d0 = cheb(nx, ny, ox, oy)
        best_r_val = -10**18
        for rx, ry in res_list:
            my_dist = cheb(nx, ny, rx, ry)
            op_dist = cheb(ox, oy, rx, ry)
            win_bonus = 120 if (nx, ny) == (rx, ry) else 0
            # Prefer resources where we are closer than opponent, and closer in absolute terms
            v = (op_dist - my_dist) * 10 + win_bonus - my_dist * 2
            # Small deterministic tiebreak: prefer resources "earlier" by coordinate
            if (v > best_r_val) or (v == best_r_val and (rx, ry) < best_r):
                best_r_val = v
                best_r = (rx, ry)
        # Also slightly avoid moving into danger near opponent by distance
        val = best_r_val + (my_d0 * 0.01)
        if (val > best_val) or (val == best_val and [dx, dy] < best_move):
            best_val = val
            best_move = [dx, dy]

    return best_move