def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x != sx or y != sy):
                resources.append((x, y))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def score_move(dx, dy, nx, ny):
        if resources:
            best = 10**9
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < best:
                    best = d
            res_score = -best
        else:
            res_score = 0
        opp_score = dist(nx, ny, ox, oy) * 0.01
        return res_score + opp_score

    best = None
    best_s = -10**18
    for dx, dy, nx, ny in moves:
        s = score_move(dx, dy, nx, ny)
        if s > best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)
    return [int(best[0]), int(best[1])]