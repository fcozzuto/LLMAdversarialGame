def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = list(map(tuple, observation.get("resources", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]
    elif unclaimed:
        best = None
        for ux, uy in unclaimed:
            if not ok(ux, uy):
                continue
            d = abs(ux - sx) + abs(uy - sy)
            if best is None or d < best[0] or (d == best[0] and (ux, uy) < best[1]):
                best = (d, (ux, uy))
        tx, ty = best[1] if best else (px, py)
    else:
        tx, ty = px, py

    def score(nx, ny):
        if not ok(nx, ny):
            return -10**9
        base = - (abs(tx - nx) + abs(ty - ny))
        base += 0.01 * (- (abs(px - nx) + abs(py - ny)))
        return base

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]