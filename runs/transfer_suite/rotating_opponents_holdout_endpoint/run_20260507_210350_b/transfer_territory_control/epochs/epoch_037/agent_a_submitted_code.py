def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def pts_to_set(v):
        s = set()
        for p in v or []:
            try:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
            except Exception:
                pass
        return s

    obstacles = pts_to_set(observation.get("obstacles"))
    unclaimed = pts_to_set(observation.get("unclaimed_cells"))
    resources = pts_to_set(observation.get("resources"))
    # If no unclaimed list is provided, fall back to resources
    targets = unclaimed if unclaimed else resources

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if targets:
            dmin = None
            for tx, ty in targets:
                if (tx, ty) in obstacles:
                    continue
                d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
                if dmin is None or d < dmin or (d == dmin and (tx, ty) < best[2]):
                    dmin = d
            score = dmin if dmin is not None else 10**18
        else:
            # No targets: prefer moving to reduce distance to opponent (if known)
            ox, oy = observation.get("opponent_position", [sx, sy]) or [sx, sy]
            ox, oy = int(ox), int(oy)
            score = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        if best is None or score < best[0]:
            best = (score, nx, ny, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[3]), int(best[4])]