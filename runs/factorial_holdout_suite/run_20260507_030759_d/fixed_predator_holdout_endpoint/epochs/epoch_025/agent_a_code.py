def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    best_t = None  # (adv, selfd, -res_collinear_bias, rx, ry)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Bias: slightly prefer resources "more aligned" with opponent being far in same direction
        # (deterministic; helps resource_denier).
        dxr = rx - sx
        dyr = ry - sy
        col = 0
        if dxr == 0 or dyr == 0:
            col = 1
        bias = -col
        key = (adv, -sd, bias, rx, ry)
        if best_t is None or key > best_t:
            best_t = key

    _, _, _, tx, ty = best_t

    # Greedy step toward target with obstacle avoidance: evaluate candidate next cells by worst-case advantage after move.
    best_move = None  # (adv_after, selfd_after, tie, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        adv2 = od2 - sd2
        # Prefer staying if equally good (denier tries to stall); discourage oscillation by slight penalty for moving away from target.
        dist_dir_pen = 0
        if sd2 > cheb(sx, sy, tx, ty):
            dist_dir_pen = 1
        key = (adv2, -sd2, -dist_dir_pen, -abs((nx - tx)) - abs((ny - ty)), dx, dy)
        if best_move is None or key > best_move:
            best_move = key

    if best_move is None:
        return [0, 0]
    return [best_move[4], best_move[5]]