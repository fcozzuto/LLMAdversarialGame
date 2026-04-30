def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if not b or len(b) < 2:
            continue
        bx, by = int(b[0]), int(b[1])
        if 0 <= bx < w and 0 <= by < h:
            obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort(key=lambda d: (d[0] == 0 and d[1] == 0, d[0], d[1]))  # deterministic preference

    def best_target_for(x, y):
        if not resources:
            return (ox, oy), cheb(x, y, ox, oy)
        best_t = resources[0]
        best_s = -10**9
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            score = (do - ds) - 0.03 * ds
            if score > best_s or (score == best_s and (rx, ry) < best_t):
                best_s = score
                best_t = (rx, ry)
        return best_t, best_s

    best_move = (0, 0)
    best_val = -10**18

    target, _ = best_target_for(sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        t = target
        # one-step lookahead: choose locally best among resources too
        if resources:
            best_loc_s = -10**18
            best_loc_t = t
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                val = (do - ds) - 0.03 * ds
                if val > best_loc_s or (val == best_loc_s and (rx, ry) < best_loc_t):
                    best_loc_s = val
                    best_loc_t = (rx, ry)
            t = best_loc_t
            base = best_loc_s
        else:
            base = -cheb(nx, ny, ox, oy)
        # slight push to approach the chosen target
        val = base - 0.01 * cheb(nx, ny, t[0], t[1])
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]