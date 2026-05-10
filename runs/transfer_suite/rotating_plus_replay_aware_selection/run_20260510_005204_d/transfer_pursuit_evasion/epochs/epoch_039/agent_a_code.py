def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in self_role) or (("pursuer" in opp_role) and ("evader" not in self_role))

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dx, best_dy = 0, 0
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(nx - ox)
        dy_ = abs(ny - oy)
        cheb = dist if dist > dy_ else dy_
        score = cheb if not self_is_pursuer else -cheb

        # small tie-breaker: prefer moves that are not heading into walls near borders
        wall_pen = 0
        if (nx == 0 or nx == w - 1) or (ny == 0 or ny == h - 1):
            wall_pen = 0.05
        score -= wall_pen if self_is_pursuer else -wall_pen

        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy
        elif score == best_score:
            if (dx, dy) < (best_dx, best_dy):
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]