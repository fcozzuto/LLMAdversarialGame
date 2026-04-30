def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick best resource by (opponent - me) advantage, then nearer to me
    target = None
    best = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 10_000 - sd
        tie = (rx, ry)
        if target is None or val > best[0] or (val == best[0] and tie < best[1]):
            best = (val, tie)
            target = (rx, ry)

    if target is None:
        target = (ox, oy)

    # Score candidate moves: go toward target while avoiding obstacles and not over-approaching opponent
    def obs_pen(x, y):
        if not obstacles:
            return 0
        p = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                return 10_000
            if d == 1:
                p += 6
            elif d == 2:
                p += 2
        return p

    opp_dist_now = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d_t = cheb(nx, ny, target[0], target[1])
        d_o = cheb(nx, ny, ox, oy)
        # discourage stepping into cells that reduce our distance to opponent too much
        delta_o = opp_dist_now - d_o
        score = d_t * 3 + (0 if delta_o <= 0 else delta_o * 20) + obs_pen(nx, ny)
        # prefer faster access to target if opponent not closer
        if cheb(nx, ny, target[0], target[1]) <= cheb(ox, oy, target[0], target[1]):
            score -= 15
        # deterministic tie-break: lowest score, then lexicographic move
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]