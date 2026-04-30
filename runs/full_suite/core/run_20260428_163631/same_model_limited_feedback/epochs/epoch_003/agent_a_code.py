def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))

    def cheb(a, b, c, d):
        ddx = a - c
        ddy = b - d
        return ddx if ddx >= 0 else -ddx if False else (ddx if ddx >= 0 else -ddx)  # overwritten below

    # fixed chebyshev without extra lines
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Select strategic target: prefer resources we can reach strictly earlier; else block by minimizing opponent advantage.
    best = None
    for rx, ry in resources:
        d_me = dist(sx, sy, rx, ry)
        d_op = dist(ox, oy, rx, ry)
        # "ahead" preference with deterministic tie-break; also bias toward central-ish resources
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        score = 0
        if d_me < d_op:
            score = 1000 - 10 * d_me - center_bias
        elif d_me == d_op:
            score = 200 - 10 * d_me - center_bias
        else:
            score = 50 - 20 * (d_op - d_me) - center_bias
        # deterministic tie-break using coordinates
        if best is None or score > best[0] or (score == best[0] and (rx, ry) < (best[1], best[2])):
            best = (score, rx, ry, d_me, d_op)
    if best is None:
        return [0, 0]

    _, tx, ty, _, _ = best

    # Evaluate immediate move: maximize progress to target, and penalize stepping onto cells that increase opponent advantage.
    best_move = (-(10**9), 0, 0)
    for dx, dy, nx, ny in candidates:
        d_now = dist(sx, sy, tx, ty)
        d_next = dist(nx, ny, tx, ty)
        progress = d_now - d_next  # positive is good
        # Opponent advantage at target after our move (we don't move opponent, but we approximate contest)
        opp_adv = dist(ox, oy, tx, ty) - dist(nx, ny, tx, ty)
        # Small preference to stay safe from obstacles indirectly: reward higher "mobility"
        mob = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                px, py = nx + ddx, ny + ddy
                if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                    mob += 1

        val = 100 * progress + 3 * opp_adv + mob
        if val > best_move[0] or (val == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (val, dx, dy)

    return [int(best_move[1]), int(best_move[2])]