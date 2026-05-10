def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = list(map(tuple, observation.get("unclaimed_cells", [])))
    if not targets:
        targets = list(map(tuple, observation.get("resources", [])))

    valid_targets = []
    for x, y in targets:
        if inb(x, y) and (x, y) not in obstacles:
            valid_targets.append((x, y))
    if valid_targets:
        tx, ty = min(valid_targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - px) + abs(ny - py)
        key = (d_t, -d_o, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]