def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move, best_val = [0, 0], None

    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not is_free(nx, ny):
                continue
            val = -md(nx, ny, cx, cy)
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
                best_val, best_move = val, [dx, dy]
        return best_move

    # Prefer resources where we are closer than opponent; edge_patrol -> deny edges by small center bias.
    factor = 1.15
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    edge_pen = 0.08

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        # Evaluate the best "swing" we can make this turn.
        best_adv = -10**9
        best_dist = 10**9
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = (od - sd * factor)
            # encourage faster convergence and slight center preference
            dist_bias = -0.03 * sd + -edge_pen * (min(rx, w - 1 - rx) + min(ry, h - 1 - ry))
            adv2 = adv + dist_bias
            if adv2 > best_adv or (adv2 == best_adv and sd < best_dist):
                best_adv, best_dist = adv2, sd
        # Mild deterrent against hugging edges from our current position
        pos_edge = edge_pen * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
        center_bias = -0.015 * md(nx, ny, center_x, center_y)
        val = best_adv + center_bias - pos_edge
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val, best_move = val, [dx, dy]

    return best_move