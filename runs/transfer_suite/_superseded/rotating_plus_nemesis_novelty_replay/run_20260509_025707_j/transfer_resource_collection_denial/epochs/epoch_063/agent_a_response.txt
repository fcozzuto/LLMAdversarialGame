def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    best_move = (None, -10**9)  # (dxdy, score)
    any_adv = False

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        best_for_cell = None  # (adv, -min_sd, od, -dist_to_opp)
        min_sd = None
        cell_any_adv = False
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if min_sd is None or sd < min_sd:
                min_sd = sd
            adv = od - sd
            if adv > 0:
                cell_any_adv = True
                key = (adv, -sd, od, -(abs(nx - ox) + abs(ny - oy)))
                if best_for_cell is None or key > best_for_cell:
                    best_for_cell = key
        if cell_any_adv:
            any_adv = True
            score = best_for_cell[0] * 1000000 + best_for_cell[1]
            if best_move[0] is None or score > best_move[1]:
                best_move = ([dx, dy], score)
        else:
            if min_sd is None:
                continue
            if not any_adv:
                # fallback: minimize our distance; break ties by being farther from opponent
                score = -min_sd * 1000 - (abs(nx - ox) + abs(ny - oy))
                if best_move[0] is None or score > best_move[1]:
                    best_move = ([dx, dy], score)

    return best_move[0] if best_move[0] is not None else [0, 0]