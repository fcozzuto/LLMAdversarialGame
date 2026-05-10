def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if inb(rx, ry) and (rx, ry) not in obs:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            candidates.append((rx, ry, sd, od))

    if not candidates:
        return [0, 0]

    # First try resources we can reach strictly before the opponent.
    ahead = []
    for rx, ry, sd, od in candidates:
        if sd < od:
            ahead.append((rx, ry, sd, od, (od - sd)))
    if ahead:
        # Maximize advantage, then minimize our distance.
        rx, ry, sd, od, adv = max(ahead, key=lambda t: (t[4], -t[2], -t[3]))
    else:
        # Otherwise, minimize how much behind we are.
        # Prefer closest resource to us if ties.
        rx, ry, sd, od = min(candidates, key=lambda t: (t[2] - t[3], t[2], -t[3]))

    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    return [dx, dy]