def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def parse_points(key):
        pts = set()
        for p in observation.get(key) or []:
            if p is None:
                continue
            if isinstance(p, dict):
                x = p.get("x", p.get(0))
                y = p.get("y", p.get(1))
            else:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = p[0], p[1]
                else:
                    continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                pts.add((x, y))
        return pts

    obstacles = parse_points("obstacles")
    unclaimed = parse_points("unclaimed_cells") or parse_points("unclaimed")
    # Prefer opponent territory if available
    targets = parse_points("opponent_territory") if (observation.get("opponent_territory") is not None) else set()
    if not unclaimed and targets:
        unclaimed = targets

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target(tx, ty):
        return -((sx - tx) * (sx - tx) + (sy - ty) * (sy - ty))

    if unclaimed:
        best = None
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            v = min(-((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)) for (tx, ty) in unclaimed)
            if v > best_val:
                best_val, best = v, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Otherwise, move toward opponent while avoiding obstacles
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = best_target(ox, oy)
        if v > best_val:
            best_val, best = v, (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]