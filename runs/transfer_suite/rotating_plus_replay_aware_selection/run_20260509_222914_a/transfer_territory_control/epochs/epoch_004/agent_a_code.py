def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = []
    for k in ("unclaimed_cells", "resources", "unclaimed_cells_list"):
        if k in observation and observation[k]:
            for p in observation[k]:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = p[0], p[1]
                    if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                        targets.append((x, y))
            if targets:
                break
    if not targets and isinstance(ox, int) and isinstance(oy, int) and valid(ox, oy):
        targets = [(ox, oy)]

    def best_score(nx, ny):
        if targets:
            bd = 10**18
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if d < bd:
                    bd = d
            return bd
        return abs(ox - nx) + abs(oy - ny)

    best = None
    best_dir = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = best_score(nx, ny)
        if best is None or s < best:
            best = s
            best_dir = (dx, dy)

    if valid(sx, sy):
        return [best_dir[0], best_dir[1]]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]