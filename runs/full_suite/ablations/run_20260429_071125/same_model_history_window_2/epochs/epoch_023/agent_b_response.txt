def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = (0, 0)
    bestv = -10**18

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy) - (cheb(nx, ny, w - 1, h - 1))
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        score = 0
        d_opp = cheb(nx, ny, ox, oy)
        score += 2 * d_opp

        # Compete for best resource by relative closeness
        best_res_gain = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp_res = cheb(ox, oy, rx, ry)
            gain = (d_opp_res - d_self)
            # Favor immediate pick
            if d_self == 0:
                gain += 30
            # Slightly discourage unreachable-adjacent cells via obstacles already filtered by inside
            if gain > best_res_gain:
                best_res_gain = gain
        score += 5 * best_res_gain

        # Tie-break: avoid stepping next to opponent if equally good
        step_pen = 0
        if d_opp <= 1:
            step_pen = 3 - d_opp
        score -= step_pen

        if score > bestv:
            bestv, bestm = score, (dx, dy)

    return [bestm[0], bestm[1]]