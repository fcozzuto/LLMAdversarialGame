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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_score = -10**9
    # Prefer a resource where we are closer than opponent (advantage), then closer overall.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_to = 10**9
        my_best_adv = -10**9
        my_best_dist = 10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_my
            if adv > my_best_adv or (adv == my_best_adv and (d_my < my_best_dist or (d_my == my_best_dist and (rx + ry) < (my_best_dist + rx + ry - (rx + ry))))):
                my_best_adv = adv
                my_best_dist = d_my
            if d_my < my_to:
                my_to = d_my
        # Encourage securing contested resources; slight bias to central-ish squares to avoid corner trapping by obstacles.
        center_bias = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
        score = my_best_adv * 1000 - my_to * 10 + center_bias
        # Tie-break deterministically: prefer move that reduces cheb distance to opponent last (keeps pressure), then lexicographic.
        op_dist = cheb(nx, ny, ox, oy)
        key = (score, -op_dist, -nx, -ny)
        if best is None or key > best:
            best = key
            best_score = score
            best_move = [dx, dy]

    return best_move