def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in self_role

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_dist_to_obstacles(x, y):
        if not obstacles:
            return 99
        md = 99
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
                if md == 1:
                    return 1
        return md

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    best_move = [0, 0]
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)
        md_ob = min_dist_to_obstacles(nx, ny)
        if nx == ox and ny == oy:
            sc = 10**9 if not is_evader else -10**9
        elif is_evader:
            sc = dist * 10.0 + mob * 0.3 + md_ob * 0.8 - (w + h) / 2 * (dist == 0)
        else:
            sc = -dist * 10.0 + mob * 0.3 + md_ob * 0.2
        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return best_move