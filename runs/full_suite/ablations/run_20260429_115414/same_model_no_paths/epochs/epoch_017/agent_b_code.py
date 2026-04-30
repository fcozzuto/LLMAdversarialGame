def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**9
        if not resources:
            # Fallback: drift away from opponent slightly while staying centered
            center = (w - 1) / 2.0
            md = cheb(nx, ny, ox, oy)
            dc = abs(nx - center) + abs(ny - center)
            return md - dc * 0.01

        my_min = 10**9
        op_min = 10**9
        best_diff = -10**9
        at_resource = False
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < my_min: my_min = myd
            if opd < op_min: op_min = opd
            d = opd - myd
            if d > best_diff: best_diff = d
            if nx == rx and ny == ry:
                at_resource = True

        # Prefer contesting resources where we are relatively closer; also reduce own distance and avoid falling behind.
        val = 0.0
        val += 120.0 if at_resource else 0.0
        val += 55.0 * best_diff
        val += -6.0 * my_min
        val += 1.5 * op_min
        val += -0.02 * cheb(nx, ny, ox, oy)  # slight preference to not collide/allow opponent to swing
        return val

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_move(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]