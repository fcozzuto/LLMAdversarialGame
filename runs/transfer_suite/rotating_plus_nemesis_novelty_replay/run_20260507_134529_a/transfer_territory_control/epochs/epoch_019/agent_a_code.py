def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_cells(key):
        out = []
        cells = observation.get(key) or []
        for p in cells:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    obstacles = set(to_cells("obstacles"))
    targets = to_cells("resources")
    if not targets:
        targets = to_cells("unclaimed_cells")
    if not targets:
        targets = to_cells("unclaimed")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if targets:
            dmin = 10**9
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if d < dmin:
                    dmin = d
            dopp = abs(ox - nx) + abs(oy - ny)
            key = (dmin, -dopp, dx, dy)
        else:
            key = (abs(ox - nx) + abs(oy - ny), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best