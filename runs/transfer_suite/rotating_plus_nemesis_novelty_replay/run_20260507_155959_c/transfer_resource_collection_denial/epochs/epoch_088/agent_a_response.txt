def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx, dy) != (0, 0):
                if inb(nx, ny) and (nx, ny) not in obs:
                    moves.append((dx, dy))
            else:
                if (sx, sy) not in obs:
                    moves.append((0, 0))
    if not moves:
        return [0, 0]

    def diag_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = None
        for dx, dy in moves:
            nsx, nsy = sx + dx, sy + dy
            d = abs(nsx - tx) + abs(nsy - ty)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        best_val = -10**18
        best_self_d = 10**9
        for rx, ry in resources:
            my_d = diag_dist(nsx, nsy, rx, ry)
            opp_d = diag_dist(ox, oy, rx, ry)
            adv = opp_d - my_d
            if my_d == 0:
                val = 10**12
            else:
                val = adv * 1000 - my_d
                if adv <= -1:
                    val -= 200 * (-adv)
            if val > best_val or (val == best_val and my_d < best_self_d):
                best_val = val
                best_self_d = my_d
        key = (-best_val, best_self_d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]