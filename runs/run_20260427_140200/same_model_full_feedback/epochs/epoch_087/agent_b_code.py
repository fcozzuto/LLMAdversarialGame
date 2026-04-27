def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        resources = [(w // 2, h // 2)]

    def min_res_dist(x, y):
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    best_our = (-(10**18), 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        our_d = min_res_dist(nx, ny)

        # Opponent best response (one step) to minimize their resource distance
        opp_best = 10**9
        for odx, ody in deltas:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            d = min_res_dist(tx, ty)
            if d < opp_best:
                opp_best = d

        # Score: maximize gap (we closer than opponent), break ties by increasing our distance from opponent
        gap = opp_best - our_d
        dist_op = cheb(nx, ny, ox, oy)
        score = gap * 100 - our_d + dist_op * 0.5
        if score > best_our[0]:
            best_our = (score, dx, dy)

    return [int(best_our[1]), int(best_our[2])]