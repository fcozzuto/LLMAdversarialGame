def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_key = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue

            best_adv = None
            best_self_d = None
            best_res = None
            for rx, ry in resources:
                self_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                adv = opp_d - self_d
                if (best_adv is None or
                    adv > best_adv or
                    (adv == best_adv and (best_self_d is None or self_d < best_self_d)) or
                    (adv == best_adv and self_d == best_self_d and (rx, ry) > (best_res[0], best_res[1]))):
                    best_adv = adv
                    best_self_d = self_d
                    best_res = (rx, ry)

            key = (best_adv, -best_self_d, -best_res[0], -best_res[1], -dx, -dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    if best_key is None:
        # All candidate cells blocked; choose safest in-bounds move (not into obstacle if possible)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]