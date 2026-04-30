def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if observation.get("remaining_resource_count", len(resources)) == 0 or not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            cand = (d, rx, ry)
            if best is None or cand < best:
                best = cand
        tx, ty = best[1], best[2]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(ox - nx) + abs(oy - ny)
        key = (dist, -opp_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]