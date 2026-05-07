def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, lo, hi):
        return lo if x < lo else (hi if x > hi else x)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    best_selfd = None
    best_tie = None

    for dx, dy in candidates:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Choose the resource that gives maximal advantage after this move
        local_best_adv = None
        local_best_sd = None
        local_best_res = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # higher is better: opponent farther than us (in chebyshev)
            if (local_best_adv is None or adv > local_best_adv or
                (adv == local_best_adv and (sd < local_best_sd or (sd == local_best_sd and (rx, ry) < local_best_res)))):
                local_best_adv, local_best_sd, local_best_res = adv, sd, (rx, ry)
        if local_best_adv is None:
            val = -10**9
            sd2 = 10**9
            tie = (0, 0)
        else:
            # Strongly prioritize winning access, then progress, then resource ordering for determinism
            val = local_best_adv * 10000 - local_best_sd
            sd2 = local_best_sd
            tie = local_best_res

        if (best_val is None or val > best_val or (val == best_val and (sd2 < best_selfd or (sd2 == best_selfd and tie < best_tie)))):
            best_val, best_selfd, best_tie = val, sd2, tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]