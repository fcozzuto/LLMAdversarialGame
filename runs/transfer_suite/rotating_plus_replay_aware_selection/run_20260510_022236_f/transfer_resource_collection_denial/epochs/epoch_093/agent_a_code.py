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

    valid = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    # Strategy change: first try to guarantee lead; if impossible, minimize the "race time" vs opponent.
    best = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we arrive earlier
        if lead > 0:
            key = (1, lead, -ds, -(rx + ry))  # prefer earlier lead, then sooner, then deterministic spatial tie-break
        else:
            # no guaranteed lead: minimize the time when the opponent can take it (race)
            key = (0, -max(ds, do), -ds, -(rx + ry))
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obs:
        return [dx, dy]

    # Obstacle avoidance: try axis-aligned move first (deterministic), then the other, else stay.
    cand = []
    if dx != 0:
        cand.append((dx, 0))
    if dy != 0:
        cand.append((0, dy))
    if dx != 0 and dy != 0:
        cand.append((dx, dy * 0))  # already axis-aligned; harmless
        cand.append((dx * 0, dy))

    for adx, ady in cand:
        nx, ny = sx + adx, sy + ady
        if inb(nx, ny) and (nx, ny) not in obs:
            return [adx, ady]
    return [0, 0]