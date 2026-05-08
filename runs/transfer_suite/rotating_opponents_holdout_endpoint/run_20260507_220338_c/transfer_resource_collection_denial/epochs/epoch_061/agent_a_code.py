def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def absd(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        closest = 10**9
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            our_d = absd(nx, ny, rx, ry)
            opp_d = absd(ox, oy, rx, ry)
            score += (opp_d - our_d)
            if our_d < closest:
                closest = our_d
        score -= closest * 0.01
        score += -abs(dx) * 0.001 - abs(dy) * 0.001
        key = (score, -closest, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]