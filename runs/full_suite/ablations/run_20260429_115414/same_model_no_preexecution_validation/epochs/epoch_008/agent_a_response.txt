def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def obs_pen(x, y):
        if not obstacles: return 0
        best = 99
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best: best = d
            if best == 0: break
        if best == 0: return 10**6
        if best == 1: return 20
        if best == 2: return 8
        return 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    opp_dist = cheb(sx, sy, ox, oy)

    # Prefer moving toward resources we are more likely to secure; otherwise contest/intercept opponent.
    best = None
    for dx, dy, nx, ny in legal_moves:
        score = 0
        if resources:
            best_resource_term = -10**18
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent (positive margin), else penalize.
                margin = od - sd
                # Also mildly prefer nearer targets overall to avoid aimless play.
                term = margin * 10 - sd
                if term > best_resource_term: best_resource_term = term
            score += best_resource_term
        else:
            # If no resources, move to reduce opponent distance
            score += (opp_dist - cheb(nx, ny, ox, oy)) * 10

        # Anticipate opponent: if we are much farther from the best resource, don't drift; contest.
        score -= obs_pen(nx, ny)

        # If opponent is very close, prioritize blocking by reducing cheb distance to opponent.
        if opp_dist <= 2:
            score += (opp_dist - cheb(nx, ny, ox, oy)) * 8 - 2 * obs_pen(nx, ny)

        # Tie-breaker: deterministic prefer staying close to center-ish relative to opponent direction
        score += -0.001 * (abs(nx - (w // 2)) + abs(ny - (h // 2)))

        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]