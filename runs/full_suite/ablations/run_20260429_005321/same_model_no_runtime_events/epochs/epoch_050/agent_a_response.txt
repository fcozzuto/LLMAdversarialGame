def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not ok(sx, sy):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    remaining = int(observation.get("remaining_resource_count") or 0)

    if resources:
        best_t = None
        best_s = -10**18
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; still keep distance small.
            # Remaining bias: earlier game -> larger advantage weight, later -> greedy.
            adv = (opd - myd)
            weight = 200 if remaining > 6 else (120 if remaining > 3 else 80)
            s = adv * weight - myd + (0 if adv > 0 else adv * 10)
            if best_t is None or s > best_s or (s == best_s and (myd < cheb(sx, sy, best_t[0], best_t[1]))):
                best_s = s
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No resources: drift toward center to reduce time to next spawn/visibility.
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Move score: closer to target, keep some distance from opponent.
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Prefer not stepping onto immediate opponent proximity if target ties.
        score = -d_to_t * 10 + d_to_o
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move