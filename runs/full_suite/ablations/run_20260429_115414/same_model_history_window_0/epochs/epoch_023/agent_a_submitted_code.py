def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(observation.get("obstacles", []))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", [])
    best = None
    for x, y in resources:
        if not inb(x, y) or (x, y) in obstacles:
            continue
        d = abs(x - sx) + abs(y - sy)
        if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
            best = (d, (x, y))
    target = best[1] if best is not None else (ox, oy)

    tx, ty = target
    curd = abs(tx - sx) + abs(ty - sy)
    best_step = (0, 0); bestd = curd + 10

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if d < bestd or (d == bestd and (dx, dy) < best_step):
            bestd = d; best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]