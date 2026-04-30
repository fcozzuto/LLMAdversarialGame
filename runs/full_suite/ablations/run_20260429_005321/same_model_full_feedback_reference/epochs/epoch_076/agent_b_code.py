def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def resource_best_from(nx, ny):
        if not resources:
            return None
        best = None
        bestv = 10**18
        for rx, ry in resources:
            v = d2(nx, ny, rx, ry)
            if v < bestv:
                bestv = v
                best = (rx, ry)
        return bestv, best

    if not resources:
        # Go to center-ish while keeping distance from opponent (avoid getting chased into obstacles).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0, -10**18)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v_center = -((nx - cx) ** 2 + (ny - cy) ** 2)
            v_opp = d2(nx, ny, ox, oy)
            score = v_center + 0.01 * v_opp
            if score > best[2]:
                best = (dx, dy, score)
        return [int(best[0]), int(best[1])]

    best_dx, best_dy = 0, 0
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        cur = resource_best_from(sx, sy)
        nxt = resource_best_from(nx, ny)
        if cur is None or nxt is None:
            continue
        cur_dist, _ = cur
        nxt_dist, _ = nxt

        # If stepping onto a resource, strongly prefer.
        on_resource = 1 if (nx, ny) in obstacles else 0
        res_gain = 0
        if (nx, ny) in set(resources):
            res_gain = 10**6

        # Prefer progress toward nearest resource; slightly avoid opponent and obstacles-clumps.
        opp_d = d2(nx, ny, ox, oy)
        progress = cur_dist - nxt_dist
        # Encourage moving away from opponent to avoid contesting near their path.
        score = res_gain + 10.0 * progress + 0.001 * opp_d

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]