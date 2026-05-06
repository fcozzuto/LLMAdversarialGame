def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            d = max(abs(nx - ox), abs(ny - oy))
            if d > bestv or (d == bestv and (dx, dy) < best):
                bestv, best = d, (dx, dy)
        return [best[0], best[1]]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_t = None
    bestv = -10**18
    for rx, ry in resources:
        sd = md(x, y, rx, ry)
        od = md(ox, oy, rx, ry)
        v = (od - sd) * 1000 - sd  # prefer resources opponent is farther from, then closer to us
        if v > bestv or (v == bestv and (sd, rx, ry) < (md(x, y, best_t[0], best_t[1]), best_t[0], best_t[1]) if best_t else True):
            bestv = v
            best_t = (rx, ry)

    tx, ty = best_t
    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if inb(nx, ny):
            sd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)
            candidates.append(( (od - sd) * 1000 - sd, -sd, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    return [candidates[0][2], candidates[0][3]]