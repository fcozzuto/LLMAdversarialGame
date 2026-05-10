def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (md(c[0], c[1], ox, oy), -md(c[0], c[1], sx, sy), c[0], c[1]))
        best = [0, 0]
        bestv = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if d < bestv or (d == bestv and (dx*dx + dy*dy) < (best[0]*best[0] + best[1]*best[1])):
                bestv = d
                best = [dx, dy]
        return best

    candidates = []
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources where we can beat opponent soon; tie-break deterministically by coordinates
        gain = od - sd
        candidates.append((gain, -sd, rx, ry))
    candidates.sort(reverse=True)
    _, _, tx, ty = candidates[0]

    # Greedy step toward chosen target with tie-break by resulting advantage
    best = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        key = (od2 - sd2, -sd2, abs(nx - ox) + abs(ny - oy), (nx == tx and ny == ty), - (dx*dx + dy*dy), nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]
    return best