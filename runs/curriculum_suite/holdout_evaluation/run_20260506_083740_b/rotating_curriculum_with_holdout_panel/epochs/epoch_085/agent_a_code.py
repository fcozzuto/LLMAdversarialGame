def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        if resources:
            best_rel = None
            best_self = None
            for r in resources:
                if not r or len(r) < 2:
                    continue
                rx, ry = int(r[0]), int(r[1])
                if not inb(rx, ry):
                    continue
                sd = md(nx, ny, rx, ry)
                od = md(ox, oy, rx, ry)
                rel = sd - od
                if best_rel is None or rel < best_rel or (rel == best_rel and sd < best_self):
                    best_rel = rel
                    best_self = sd
            rel_score = best_rel
            self_close = best_self
        else:
            rel_score = 0
            self_close = md(nx, ny, ox, oy)

        opp_close = md(nx, ny, ox, oy)
        dx_dy_penalty = (dx != 0 or dy != 0)

        score = (rel_score if resources else 0, self_close, -opp_close, -int(dx_dy_penalty))
        if best is None or score < best:
            best = score
            best_move = [dx, dy]

    return best_move