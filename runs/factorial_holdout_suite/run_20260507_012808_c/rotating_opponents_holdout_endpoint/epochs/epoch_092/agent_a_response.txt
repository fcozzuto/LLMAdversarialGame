def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    opp_bias = 3.0
    denier_mode = observation.get("opponent_role", "") == "resource_denier"
    if denier_mode:
        opp_bias = 4.5

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0.0
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_self == 0:
                score_term = 200.0
            else:
                score_term = 120.0 / (1.0 + d_self)
            contest_term = (d_opp - d_self)  # positive means we arrive no later than opp
            val += score_term + opp_bias * contest_term

        # small preference to avoid getting stuck
        if (nx, ny) in resources:
            val += 50.0
        if denier_mode and cheb(nx, ny, ox, oy) <= cheb(sx, sy, ox, oy):
            val += 2.0

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]