def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = w // 2, h // 2
    best_r = None
    best_val = None

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)

        # Reward getting closer than opponent; also reward central positions a bit.
        d_adv = do - ds

        # Predict opponent's immediate step towards this resource; if blocked/outside, give bonus.
        step_x = 0 if rx == ox else (1 if rx > ox else -1)
        step_y = 0 if ry == oy else (1 if ry > oy else -1)
        pred_ox, pred_oy = ox + step_x, oy + step_y
        opp_block_bonus = 3.0 if (not (0 <= pred_ox < w and 0 <= pred_oy < h)) or ((pred_ox, pred_oy) in obstacles) else 0.0

        # Mild preference for earlier progress and centrality (tie-break).
        centrality = cheb(rx, ry, cx, cy)
        val = 10.0 * d_adv + opp_block_bonus + (-0.08 * ds) + (-0.01 * centrality)

        if best_val is None or val > best_val:
            best_val = val
            best_r = (rx, ry)
        elif val == best_val and best_r is not None:
            # Deterministic tie-break: closer to center, then smaller ds, then lexicographic.
            brx, bry = best_r
            if cheb(rx, ry, cx, cy) < cheb(brx, bry, cx, cy):
                best_r = (rx, ry)
            elif cheb(rx, ry, cx, cy) == cheb(brx, bry, cx, cy):
                if ds < cheb(sx, sy, brx, bry):
                    best_r = (rx, ry)
                elif ds == cheb(sx, sy, brx, bry):
                    if (rx, ry) < (brx, bry):
                        best_r = (rx, ry)

    tx, ty = best_r

    # If we're already on the target, try to move to reduce distance to the next closest resource; otherwise stay.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            candidates.append((dx, dy, cheb(nx, ny, tx, ty)))
    if not candidates:
        return [0, 0]

    # Deterministic: min distance to target; tie-break by move ordering (given by moves list).
    best_move = None
    best_d = None
    for dx, dy, nd in candidates:
        if best_d is None or nd < best_d:
            best_d = nd
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]