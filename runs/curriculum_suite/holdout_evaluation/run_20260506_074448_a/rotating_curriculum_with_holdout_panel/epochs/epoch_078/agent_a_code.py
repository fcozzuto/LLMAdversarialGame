def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    valid = []
    for rx, ry in resources:
        if (rx, ry) not in obstacles:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    best_win = None
    best_win_key = None
    best_deny = None
    best_deny_key = None
    for rx, ry in valid:
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        cent = -(abs(rx - cx) + abs(ry - cy))
        win_key = (-(oppd - myd), cent, myd, rx, ry)  # prefer we reach earlier by margin
        deny_key = (oppd, myd, cent, rx, ry)        # prefer what opponent can reach soon
        if best_win_key is None or win_key > best_win_key:
            best_win_key = win_key
            best_win = (rx, ry)
        if best_deny_key is None or deny_key < best_deny_key:
            best_deny_key = deny_key
            best_deny = (rx, ry)

    # Decide mode: if we have a clear winning resource, chase it; else contest opponent's closest.
    win_rx, win_ry = best_win
    deny_rx, deny_ry = best_deny
    myd_win = man(sx, sy, win_rx, win_ry)
    oppd_win = man(ox, oy, win_rx, win_ry)
    mode_deny = not (myd_win <= oppd_win - 1)

    tx, ty = (deny_rx, deny_ry) if mode_deny else (win_rx, win_ry)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_t = man(nx, ny, tx, ty)
        dist_o = man(nx, ny, ox, oy)
        # If denying, add pressure toward opponent's nearest resource; also keep some separation.
        if mode_deny:
            dist_op_target = man(nx, ny, deny_rx, deny_ry)
            key = (dist_t, -dist_op_target, abs(nx - ox) + abs(ny - oy), dist_o, tx, ty, dx, dy)
        else:
            key = (dist_t, dist_o, abs(nx - ox) + abs(ny - oy), tx, ty, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]