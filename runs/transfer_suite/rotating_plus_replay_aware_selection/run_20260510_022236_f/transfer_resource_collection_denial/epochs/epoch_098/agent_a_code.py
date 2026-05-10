def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = [(int(x), int(y)) for x, y in resources if inb(int(x), int(y)) and (int(x), int(y)) not in obs]
    if not valid:
        return [0, 0]

    midy = (h - 1) / 2.0
    best = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # Prefer guaranteed advantage; then quickest capture; then central-ish.
        key = (lead, -ds, -(abs(ry - midy)))
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        our_after = cheb(nx, ny, tx, ty)
        opp_after = cheb(ox, oy, tx, ty)
        lead_after = opp_after - our_after
        mkey = (lead_after, -our_after, -(abs(ny - midy)), -abs(nx - sx) - abs(ny - sy))
        if bestm is None or mkey > bestm[0]:
            bestm = (mkey, dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]