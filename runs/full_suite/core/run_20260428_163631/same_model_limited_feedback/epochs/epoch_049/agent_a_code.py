def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cd(a, b):  # Chebyshev distance for grid with diagonal
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if resources:
        best = None
        bx = by = 0
        for rx, ry in resources:
            sd = cd((sx, sy), (rx, ry))
            od = cd((ox, oy), (rx, ry))
            diff = od - sd
            if best is None or diff > best[0] or (diff == best[0] and sd < best[1]) or (diff == best[0] and sd == best[1] and (rx, ry) < (bx, by)):
                best = (diff, sd)
                bx, by = rx, ry
        tx, ty = bx, by
    else:
        # No resources known: move toward opponent corner (deterministic fallback)
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            d0 = cd((nx, ny), (tx, ty))
            d1 = cd((sx, sy), (tx, ty))
            # Prefer reducing distance; slight tie-break toward becoming closer than opponent
            my_ahead = cd((ox, oy), (tx, ty)) - d0
            val = (d1 - d0, my_ahead, -d0, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2))
        else:
            d0 = cd((nx, ny), (tx, ty))
            val = (-d0, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]