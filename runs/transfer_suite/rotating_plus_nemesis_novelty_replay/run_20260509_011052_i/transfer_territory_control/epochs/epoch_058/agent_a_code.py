def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        res_term = 0
        if resources:
            dmin = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            res_term = -dmin

        adj_self = 0
        if self_terr:
            for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if (nx + ax, ny + ay) in self_terr:
                    adj_self += 1

        opp_term = dist(nx, ny, ox, oy)
        score = res_term + 3 * adj_self + 0.01 * opp_term

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]