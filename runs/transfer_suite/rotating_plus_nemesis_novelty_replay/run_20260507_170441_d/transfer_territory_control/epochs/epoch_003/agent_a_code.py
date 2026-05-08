def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y):
                obs_set.add((x, y))
        except:
            pass

    un_set = set()
    cells = observation.get("unclaimed_cells", None)
    if cells is None:
        cells = observation.get("resources", None)
    if cells is not None:
        for p in cells or []:
            try:
                x, y = int(p[0]), int(p[1])
                if in_bounds(x, y) and (x, y) not in obs_set and (x, y) != (sx, sy):
                    un_set.add((x, y))
            except:
                pass

    if un_set:
        tx, ty = min(un_set, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        cand = (d, abs(dx) + abs(dy))
        if best is None or cand < best[0]:
            best = (cand, [dx, dy])

    return best[1] if best is not None else [0, 0]