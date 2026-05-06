def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (0, 0)
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Favor contested resources: smallest (self_d - opp_d), then closest self_d
        move_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (sd - od, sd)
            if move_best is None or key < move_best:
                move_best = key
        if best_key is None or move_best < best_key:
            best_key, best = move_best, (dx, dy)
    return [best[0], best[1]]