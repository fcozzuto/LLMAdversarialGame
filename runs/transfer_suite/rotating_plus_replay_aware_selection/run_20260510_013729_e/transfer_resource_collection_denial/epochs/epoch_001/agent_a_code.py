def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacle_set = set((x, y) for x, y in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w // 2), (h // 2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacle_set:
            continue
        mdist = abs(tx - nx) + abs(ty - ny)
        odist = abs(ox - nx) + abs(oy - ny)
        tie_break = (0 if (dx == desired_dx and dy == desired_dy) else 1)
        candidates.append((mdist, tie_break, -odist, nx, ny, dx, dy))

    candidates.sort()
    return [candidates[0][5], candidates[0][6]] if candidates else [0, 0]