def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            if best is None or d < best:
                best = d
                bestm = [mx, my]
        return bestm if best is not None else [0, 0]

    def dman(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx + dy

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    best_val = None
    best_move = [0, 0]
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate next position: choose target we can arrive at first; otherwise
        # choose one with maximal denial margin.
        cur_best = None
        for rx, ry in resources:
            sd = dman(nx, ny, rx, ry)
            od = dman(ox, oy, rx, ry)
            # "Reach-first" bonus; denial when opponent is closer.
            margin = (od - sd)
            reach_first = 1 if sd <= od else 0
            # Mild center preference to reduce oscillation.
            center_bias = -0.001 * ((center_x - rx) ** 2 + (center_y - ry) ** 2)
            val = (1000 * reach_first) + margin * 10 - sd * 0.5 + center_bias
            if cur_best is None or val > cur_best:
                cur_best = val

        if best_val is None or cur_best > best_val:
            best_val = cur_best
            best_move = [mx, my]

    return [int(best_move[0]), int(best_move[1])]