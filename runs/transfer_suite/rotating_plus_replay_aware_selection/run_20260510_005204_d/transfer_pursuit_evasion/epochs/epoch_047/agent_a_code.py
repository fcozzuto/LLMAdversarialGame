def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_away = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)
    opp_away = ("evader" in opp_role) or ("runner" in opp_role) or ("escape" in opp_role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def clamp_move(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if legal(nx, ny):
            return nx, ny
        return x, y

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def corner_metric(x, y, want_far):
        mc = min if want_far else max
        target = mc([abs(x - cx) + abs(y - cy) for cx, cy in corners], default=0)
        return target

    def opponent_next(px, py, ex, ey):
        best = None
        bestv = None
        for dx, dy in neigh:
            nx, ny = clamp_move(px, py, dx, dy)
            v = dist2(ex, ey, nx, ny)
            if opp_away:
                v = v  # maximize distance^2
            else:
                v = -v  # minimize distance^2
            # Tie-break deterministically: bias toward/away from closest corner
            corner = corner_metric(nx, ny, want_far=opp_away)
            v = (v, corner)
            if best is None or v > bestv:
                bestv, best = v, (nx, ny)
        return best[0], best[1]

    best_move = (0, 0)
    best_score = None

    for dx, dy in neigh:
        nx, ny = clamp_move(sx, sy, dx, dy)
        onx, ony = opponent_next(ox, oy, nx, ny)

        d2 = dist2(nx, ny, onx, ony)
        # score: if we are pursuer, minimize distance; if evader, maximize distance
        if self_away:
            score = d2
            # extra: move to maximize distance from opponent's "effective pull" corner
            score = (score, corner_metric(nx, ny, want_far=True))
        else:
            score = (-d2, corner_metric(nx, ny, want_far=False))

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]