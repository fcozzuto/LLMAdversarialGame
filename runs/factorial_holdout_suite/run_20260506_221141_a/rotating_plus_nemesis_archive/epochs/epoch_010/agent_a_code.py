def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if res:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = None
            for r in res:
                rx, ry = r[0], r[1]
                dd = man(nx, ny, rx, ry)
                if d is None or dd < d:
                    d = dd
            key = (d, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is not None:
            return [best[1], best[2]]

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        key = (-d, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]] if best is not None else [0, 0]