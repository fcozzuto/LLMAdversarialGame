def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in obstacles:
        resources = []

    if resources:
        man = lambda a, b, c, d: abs(a - c) + abs(b - d)
        best = min(resources, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))
        tx, ty = best
        if (sx, sy) == (tx, ty):
            return [0, 0]

        dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        best_move = None
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = man(nx, ny, tx, ty)
                if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
                    best_val = val
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward opponent if possible, else stay.
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_move = (0, 0)
    best_val = abs(sx - ox) + abs(sy - oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            val = abs(nx - ox) + abs(ny - oy)
            if val < best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]