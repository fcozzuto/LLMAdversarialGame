def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacle_set

    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_score = None

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate move by best advantage it creates vs opponent over all remaining resources
        best_adv = None
        best_sd2 = None
        best_row_pen = None
        for rx, ry in resources:
            if (rx, ry) in obstacle_set:
                continue
            sd2 = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd2  # positive means we are closer to that resource than opponent
            row_pen = abs(ry - oy)  # prefer resources far from opponent's sweep row
            key2 = (adv, -row_pen, -sd2, rx, ry)
            if best_adv is None or key2 > (best_adv, best_row_pen, best_sd2, -1, -1):
                best_adv = adv
                best_sd2 = sd2
                best_row_pen = row_pen

        if best_adv is None:
            continue

        # Encourage moving to a resource soon, but avoid overcommitting when it aligns with opponent's row
        score = (best_adv, -best_row_pen, -best_sd2, -abs(nx - ox), -abs(ny - oy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move