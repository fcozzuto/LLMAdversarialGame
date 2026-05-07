def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best_score = None
    best_t = None

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)

        step_x = 0 if rx == ox else (1 if rx > ox else -1)
        step_y = 0 if ry == oy else (1 if ry > oy else -1)
        pred_ox, pred_oy = ox + step_x, oy + step_y
        opp_block_bonus = 3.5 if (not (0 <= pred_ox < w and 0 <= pred_oy < h)) or ((pred_ox, pred_oy) in obstacles) else 0.0

        self_central = -(abs(sx - cx) + abs(sy - cy))
        res_central = -(abs(rx - cx) + abs(ry - cy))
        score = (do - ds) + opp_block_bonus + 0.02 * res_central + 0.005 * self_central - 0.001 * ds
        if best_score is None or score > best_score or (score == best_score and (rx, ry) < best_t):
            best_score = score
            best_t = (rx, ry)

    rx, ry = best_t
    tx = 0 if rx == sx else (1 if rx > sx else -1)
    ty = 0 if ry == sy else (1 if ry > sy else -1)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Prefer moves that reduce distance to target; break ties by aligning with greedy direction.
        new_d = cheb(nx, ny, rx, ry)
        align = abs(dx - tx) + abs(dy - ty)
        candidates.append((new_d, align, nx, ny))
    candidates.sort()
    if not candidates:
        return [0, 0]
    _, _, nx, ny = candidates[0]
    return [nx - sx, ny - sy]