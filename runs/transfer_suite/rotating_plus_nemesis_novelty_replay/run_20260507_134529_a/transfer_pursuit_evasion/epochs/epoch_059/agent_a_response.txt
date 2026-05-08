def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role") or "").lower()
    self_is_evader = "evader" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_dist_to_obstacle(x, y):
        if not obstacles:
            return 99
        md = 99
        for ax, ay in obstacles:
            dd = abs(x - ax) + abs(y - ay)
            if dd < md:
                md = dd
                if md == 1:
                    break
        return md

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    sign = 1 if self_is_evader else -1
    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        sc = sign * d + 0.02 * mobility(nx, ny) + 0.001 * min_dist_to_obstacle(nx, ny)
        if sc > best_sc or (sc == best_sc and (best is None or (dx, dy) < best)):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]