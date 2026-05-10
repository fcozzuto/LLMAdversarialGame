def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_for_target(tx, ty):
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        return (od - sd, -sd, -tx, -ty)

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        for mx, my in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [mx, my]
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        k = best_for_target(rx, ry)
        if best_key is None or k > best_key:
            best_key = k
            best_target = (rx, ry)

    tx, ty = best_target
    # Prefer move that decreases Chebyshev distance to target; break ties by "win race" advantage.
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_mkey = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        sd1 = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # tuple: (improve, race_adv, prefer closer, prefer lex)
        mkey = (sd2 < sd1, (od - sd2), -sd2, -nx, -ny, -mx, -my)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (mx, my)

    if best_mkey is None:
        return [0, 0]
    return [best_move[0], best_move[1]]