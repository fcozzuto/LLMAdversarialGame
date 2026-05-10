def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets we can reach earlier; otherwise still prefer "most delayed" for opponent.
        lead = do - ds
        time_bias = 0
        if tr > 0:
            time_bias = 0.05 * (ds <= tr) - 0.02 * (do <= tr)
        score = lead + time_bias - 0.01 * ds
        cand = (score, -do, -ds, rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, _, tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            # Mildly avoid getting too close to opponent unless it helps reach target.
            oppd = cheb(nx, ny, ox, oy)
            moves.append((d, -oppd, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort()
    return [moves[0][2], moves[0][3]]