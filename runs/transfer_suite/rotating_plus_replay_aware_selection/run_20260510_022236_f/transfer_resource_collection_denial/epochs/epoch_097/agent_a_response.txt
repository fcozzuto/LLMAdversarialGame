def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))
    remaining = int(observation.get("remaining_resource_count", len(resources)))

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best_t = None
    for rx, ry in valid:
        ds = cheb_dist(sx, sy, rx, ry)
        do = cheb_dist(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        tempo = ds - (0 if remaining <= 4 else min(2, ds // max(1, tr + 1)))
        midy = -abs(ry - (h - 1) / 2.0)
        # Encourage faster grabs when time is short; otherwise maximize contest lead.
        time_bias = 0 if tr > 10 else (ds)
        score = (lead, -tempo, midy, -time_bias)
        if best_t is None or score > best_t[0]:
            best_t = (score, rx, ry, ds, do)
    _, tx, ty, ds0, do0 = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds = cheb_dist(nx, ny, tx, ty)
        do = cheb_dist(ox, oy, tx, ty)
        lead = do - ds
        step_cost = ds
        # Slight preference to reduce both axes motion when far from target centerline.
        center_bias = -abs(ny - (h - 1) / 2.0) * 0.01
        score = (lead, -step_cost, center_bias, -abs(dx) - abs(dy) * 0.001)
        if best_m is None or score > best_m[0]:
            best_m = (score, dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[1]), int(best_m[2])]