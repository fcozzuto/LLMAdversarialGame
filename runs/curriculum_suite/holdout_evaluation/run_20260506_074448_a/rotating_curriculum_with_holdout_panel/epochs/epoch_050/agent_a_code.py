def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list}
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best[0] < 10**9 else [0, 0]

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_for_move = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            val = op_d - my_d
            if val > best_for_move:
                best_for_move = val
        # tie-break: prefer smaller my distance to the best resource
        if best_for_move > best_score:
            best_score = best_for_move
            best_move = (dx, dy)
        elif best_for_move == best_score:
            # deterministic tie-break: closer to opponent-weaker resource
            if best_move != (dx, dy):
                my_best = 10**9
                for r in resources:
                    rx, ry = r[0], r[1]
                    my_best = min(my_best, man(nx, ny, rx, ry))
                cur_best = 10**9
                bx, by = best_move
                cx, cy = sx + bx, sy + by
                for r in resources:
                    rx, ry = r[0], r[1]
                    cur_best = min(cur_best, man(cx, cy, rx, ry))
                if my_best < cur_best:
                    best_move = (dx, dy)

    if best_score < -10**17:
        return [0, 0]
    return [best_move[0], best_move[1]]