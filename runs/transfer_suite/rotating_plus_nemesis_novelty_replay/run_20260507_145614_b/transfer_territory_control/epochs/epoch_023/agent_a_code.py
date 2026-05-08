def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) if p and len(p) >= 2)
    resources = [tuple(p) for p in observation.get("resources", []) if p and len(p) >= 2]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            dres = abs(nx - (w // 2)) + abs(ny - (h // 2))

        dopp = abs(nx - ox) + abs(ny - oy)
        key = (dres, -dopp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best