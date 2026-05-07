def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    target = None
    if resources:
        best_d = None
        best_cell = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_cell):
                best_d = d
                best_cell = (rx, ry)
        target = best_cell

    # If no resources, drift toward center while keeping distance from opponent.
    cx, cy = w // 2, h // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is not None:
            dist = abs(target[0] - nx) + abs(target[1] - ny)
        else:
            dist = abs(cx - nx) + abs(cy - ny)
        opp_pen = abs(ox - nx) + abs(oy - ny)
        # Higher is better.
        val = -dist + 0.001 * opp_pen
        if (nx, ny) != (sx, sy):
            val += 0.01
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]