def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def dist(a, b, c, d):
        # Chebyshev is natural with diagonal moves
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def adj_obst(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    # Predict opponent's nearest-resource target
    opp_target = None
    best_od = None
    for r in resources:
        od = dist(ox, oy, r[0], r[1])
        if best_od is None or od < best_od or (od == best_od and (r[0], r[1]) < (opp_target[0], opp_target[1])):
            best_od = od
            opp_target = r

    tx, ty = opp_target[0], opp_target[1]

    # Interception: move that makes us as close to opponent's target as possible,
    # while keeping advantage over opponent's distance.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None  # (score, dx, dy, nx, ny)

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        sd = dist(nx, ny, tx, ty)
        od = dist(nx, ny, ox, oy)  # closer to opponent can disrupt
        self_to_t = dist(nx, ny, tx, ty)
        opp_to_t = dist(ox, oy, tx, ty)
        adv = (opp_to_t - self_to_t)  # positive if we are closer to target than opponent currently
        obst_pen = adj_obst(nx, ny)
        # Strongly favor reducing distance to target; add advantage and disruption.
        score = (1000 * (-self_to_t) + 80 * adv + 10 * (-od) - 12 * obst_pen, -sd, nx, ny, dx, dy)
        if best is None or score > best[0]:
            best = (score, dx, dy, nx, ny)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]