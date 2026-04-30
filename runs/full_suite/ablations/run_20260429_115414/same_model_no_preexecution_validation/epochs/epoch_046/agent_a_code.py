def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if in_bounds(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        # Choose resource maximizing "tempo advantage" (opponent farther than us), then closeness to center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_key = None
        for x, y in resources:
            d_me = cheb(sx, sy, x, y)
            d_op = cheb(ox, oy, x, y)
            adv = d_op - d_me
            center = abs(x - cx) + abs(y - cy)
            key = (adv, -d_me, -center)
            if best_key is None or key > best_key:
                best_key = key
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if not in_bounds(tx, ty):
            # deterministically pick nearest in-bounds cell to center
            best = None
            best_d = None
            cx, cy = (w - 1) // 2, (h - 1) // 2
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    x, y = cx + dx, cy + dy
                    if in_bounds(x, y):
                        d = abs(dx) + abs(dy)
                        if best_d is None or d < best_d:
                            best_d = d
                            best = (x, y)
            if best is not None:
                tx, ty = best

    # Move one step toward target; if blocked, pick best among valid moves by improved objective
    cur_d_me = cheb(sx, sy, tx, ty)
    cur_d_op = cheb(ox, oy, tx, ty)
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        # Encourage taking resources before opponent; slight penalty for moving away from them
        score = (cur_d_op - d_me) * 1000 - d_me
        # If already very close, prefer staying/finishing path
        score += -abs(nx - tx) - abs(ny - ty)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]