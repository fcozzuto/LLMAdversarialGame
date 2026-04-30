def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def dist(a, b, c, d):
        adx = a - c
        ady = b - d
        if adx < 0: adx = -adx
        if ady < 0: ady = -ady
        return adx if adx > ady else ady  # Chebyshev for diagonal reach

    def clamp1(v):
        return -1 if v < -1 else (1 if v > 1 else v)

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist(x, y, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (0 if sd <= od else 1, sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = clamp1(tx - x)
    dy = clamp1(ty - y)

    candidates = []
    candidates.append((dx, dy))
    candidates.append((dx, 0))
    candidates.append((0, dy))
    candidates.append((0, 0))
    if dx != 0 and dy != 0:
        candidates.append((dx, -dy))
        candidates.append((-dx, dy))

    for mdx, mdy in candidates:
        nx, ny = x + mdx, y + mdy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        return [int(mdx), int(mdy)]

    return [0, 0]