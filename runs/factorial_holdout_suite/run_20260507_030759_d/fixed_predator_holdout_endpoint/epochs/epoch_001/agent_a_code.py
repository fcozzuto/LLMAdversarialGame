def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx + dy

    candidates = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds  # prefer resources closer than opponent
        candidates.append((adv, ds, rx, ry))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    _, _, tx, ty = candidates[0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, tx, ty)
        oppd = dist(ox, oy, tx, ty)
        score = (d, -max(0, oppd - d), abs(dx) + abs(dy), dx, dy)
        if score < best:
            best = score
    return [best[3], best[4]]