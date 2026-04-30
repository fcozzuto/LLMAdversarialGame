def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = moves

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def adj_to_obstacle(x, y):
        p = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in blocked:
                p += 1
        return p

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -adj_to_obstacle(nx, ny) - cheb(nx, ny, ox, oy) * 0.01
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    opp_factor = 1.0 + (len(resources) > 6) * 0.15
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_pen = adj_to_obstacle(nx, ny) * 0.25
        opp_pen = cheb(nx, ny, ox, oy) * 0.02

        best_res_score = -10**18
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; tie-break by our absolute distance.
            res_score = (d_opp - d_my) * opp_factor - d_my * 0.01
            # Mild bias to go "downstream" toward bottom-right area (common opposite-corner pressure).
            res_score += (nx + ny) * 0.001
            if res_score > best_res_score:
                best_res_score = res_score

        val = best_res_score - my_pen - opp_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]