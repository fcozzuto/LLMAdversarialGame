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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)

        # Predict whether opponent's next greedy step towards this resource is blocked.
        step_x = 0 if rx == ox else (1 if rx > ox else -1)
        step_y = 0 if ry == oy else (1 if ry > oy else -1)
        pred_ox, pred_oy = ox + step_x, oy + step_y
        opp_block_bonus = 3.0 if (not (0 <= pred_ox < w and 0 <= pred_oy < h)) or ((pred_ox, pred_oy) in obstacles) else 0.0

        # Prefer claiming advantage; break ties by centrality and keeping distance from edges.
        edge_pref = abs(rx - cx) + abs(ry - cy)
        score = (ds - do) - opp_block_bonus + 0.05 * edge_pref

        if best is None or score < best[0]:
            best = (score, rx, ry)

    _, tx, ty = best
    # Choose move that greedily reduces our distance to the target while avoiding obstacles/out-of-bounds.
    best_move = (0, 0)
    best_d = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if best_d is None or d < best_d or (d == best_d and (mx, my) < best_move):
            best_d = d
            best_move = (mx, my)

    return [best_move[0], best_move[1]]