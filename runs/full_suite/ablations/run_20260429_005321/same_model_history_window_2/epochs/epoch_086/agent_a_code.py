def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # No remaining resources: drift toward opponent-reachable center-ish point deterministically
        tx, ty = (w // 2), (h // 2)
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (-d, nx, ny)
            if best_key is None or key > best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_move = (0, 0)
    best_key = None

    # 1-step lookahead: choose move that maximizes our relative access to the best contested resource
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_adv = None
        best_dme = None
        best_rx = None
        best_ry = None

        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me
            if (best_adv is None or adv > best_adv or
                (adv == best_adv and (d_me < best_dme or (d_me == best_dme and (rx, ry) < (best_rx, best_ry))))):
                best_adv, best_dme, best_rx, best_ry = adv, d_me, rx, ry

        # Secondary tie-breaks: closer to that resource, and steer to reduce our own distance sum to all resources (lightweight)
        sum_d = 0
        for rx, ry in resources:
            sum_d += cheb(nx, ny, rx, ry)
            if sum_d > 200:  # keep it bounded and fast/deterministic
                break

        key = (best_adv, -best_dme, -sum_d, best_rx, best_ry)
        if best_key is None or key > best_key:
            best_key, best_move = key, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]