def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                disto = abs(nx - ox) + abs(ny - oy)
                sc = disto
                if best is None or sc > best[0]:
                    best = (sc, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    def mindist(nx, ny):
        m = None
        for rx, ry in resources:
            d = abs(nx - rx) + abs(ny - ry)
            if m is None or d < m:
                m = d
        return m if m is not None else 0

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dres = mindist(nx, ny)
            dop = abs(nx - ox) + abs(ny - oy)
            sc = -dres + 0.3 * dop
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]