def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    dlist = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Bias to prevent the evader/pursuer from escaping along the nearest wall axis.
    wall_bias_x = 0
    if ox <= 1:
        wall_bias_x = 1
    elif ox >= w - 2:
        wall_bias_x = -1
    wall_bias_y = 0
    if oy <= 1:
        wall_bias_y = 1
    elif oy >= h - 2:
        wall_bias_y = -1

    best_move = [0, 0]
    best_sc = -10**18

    for dx, dy in dlist:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        # Core score: reduce Euclidean distance (approx) to opponent.
        ddx, ddy = ox - nx, oy - ny
        dist2 = ddx * ddx + ddy * ddy

        # Secondary: alignment with opponent direction and wall pressure.
        align = 0
        if dx != 0 and (ox - sx) != 0:
            align += 3 if (dx > 0) == ((ox - sx) > 0) else -3
        if dy != 0 and (oy - sy) != 0:
            align += 3 if (dy > 0) == ((oy - sy) > 0) else -3

        wall_press = 0
        if wall_bias_x != 0 and dx != 0:
            wall_press += 2 if (dx > 0) == (wall_bias_x > 0) else -2
        if wall_bias_y != 0 and dy != 0:
            wall_press += 2 if (dy > 0) == (wall_bias_y > 0) else -2

        # Small obstacle proximity penalty for moving near obstacles (discourages getting stuck).
        near_pen = 0
        for bx, by in blocked:
            md = abs(bx - nx) + abs(by - ny)
            if md <= 2:
                near_pen -= (3 - md)

        # Prefer staying closer than current position.
        cur_ddx, cur_ddy = ox - sx, oy - sy
        cur_dist2 = cur_ddx * cur_ddx + cur_ddy * cur_ddy
        improvement_bonus = 5 if dist2 < cur_dist2 else (-2 if dist2 > cur_dist2 else 0)

        sc = (-dist2) * 10 + align + wall_press + near_pen + improvement_bonus

        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return best_move