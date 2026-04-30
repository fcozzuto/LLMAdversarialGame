def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    def read_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
            p = v.get("position", None)
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return 0, 0

    sx, sy = read_xy(observation.get("self_position", [0, 0]))
    ox, oy = read_xy(observation.get("opponent_position", [0, 0]))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        x, y = read_xy(p)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        x, y = read_xy(p)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            md = None
            for rx, ry in resources:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if md is None or d < md:
                    md = d
        else:
            md = 0

        od = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        cand = (md if resources else 0, -od, i, dx, dy)
        if best is None or cand < best:
            best = cand

    if best is not None:
        return [best[3], best[4]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]