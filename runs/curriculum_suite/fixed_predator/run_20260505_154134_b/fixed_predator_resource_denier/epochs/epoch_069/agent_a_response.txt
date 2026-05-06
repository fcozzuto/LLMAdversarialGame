def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in moves:
            v = -cheb(nx, ny, tx, ty) - 0.01 * cheb(nx, ny, ox, oy)
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    best_dx, best_dy = 0, 0
    best_score = None

    # Evaluate each move by its effect on the best "resource contest" after the move.
    # Value: favor moving toward resources; if opponent is closer, strongly prefer denying
    # by reducing their advantage (opp_d - self_d).
    for dx, dy, nx, ny in moves:
        cur_best = None
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Higher is better.
            # Baseline: we want to be closer (opp_d - our_d large).
            # Also prefer smaller combined distance so we actually reach.
            contest = (opp_d - our_d)
            reach = -(our_d + 0.35 * cheb(nx, ny, sx, sy))  # slight "keep moving"
            # If opponent already closer, prioritize denying their advantage.
            deny_boost = 2.5 if opp_d < our_d else 0.0
            score = contest + reach + deny_boost
            # If we're at the resource, it's dominant.
            if our_d == 0:
                score += 100.0
            if cur_best is None or score > cur_best:
                cur_best = score
        # Tie-break: reduce distance to opponent slightly to avoid being penned.
        tie = -cheb(nx, ny, ox, oy) * 0.01
        total = cur_best + tie
        if best_score is None or total > best_score:
            best_score = total
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]