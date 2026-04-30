def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best_r = resources[0]
        best_key = None
        for r in resources:
            dself = cheb((sx, sy), r)
            dopp = cheb((ox, oy), r)
            key = (dopp - dself, -dself, -r[0], -r[1])
            if best_key is None or key > best_key:
                best_key = key
                best_r = r
        tx, ty = best_r

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    def obs_block_pen(nx, ny):
        if (nx, ny) in obstacles:
            return 10**6
        p = 0
        for ax, ay in obstacles:
            d = abs(nx - ax) + abs(ny - ay)
            if d == 0:
                return 10**6
            p += (3 - min(d, 3))  # closer obstacles -> bigger penalty
        return p

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dmy = cheb((nx, ny), (tx, ty))
        dopp = cheb(opp_pos, (tx, ty))
        my_adv_now = dopp - dmy  # higher is better
        cur_d = cheb(my_pos, (tx, ty))
        improved = cur_d - dmy  # prefer moving closer
        res_near = 0
        if resources:
            for r in resources:
                if r == (nx, ny):
                    res_near += 6
                else:
                    res_near -= 0.5 * (cheb((nx, ny), r) == 1)
        score = (10 * my_adv_now) + (2 * improved) - obs_block_pen(nx, ny) + res_near - 0.01 * (dmy + cheb(opp_pos, (nx, ny)))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]