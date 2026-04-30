def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if resources:
            best = None
            # Bias to resources the opponent is farther from (contested avoidance).
            # alpha increases when opponent is closer to our side.
            alpha = 0.9
            opp_pressure = cheb(ox, oy, sx, sy)
            if opp_pressure <= 2:
                alpha = 1.3
            elif opp_pressure >= 6:
                alpha = 0.6
            for rx, ry in resources:
                ds = cheb(sx, sy, rx, ry)
                do = cheb(ox, oy, rx, ry)
                score = ds - alpha * do
                # Prefer closer overall as tie-breaker
                if best is None or score < best[0] or (score == best[0] and ds < best[1]):
                    best = (score, ds, rx, ry)
            return (best[2], best[3])
        # If no visible resources, head to center.
        return (w // 2, h // 2)

    tx, ty = best_target()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_cost = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Move cost: prioritize reducing distance to target; add repulsion from opponent to avoid collision/steal.
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Strongly avoid stepping onto tiles adjacent to opponent when we're not already closer.
        proximity_pen = 0
        if d_to_o <= 1:
            proximity_pen = 6
        # Small preference to keep moving rather than staying if equal.
        stay_pen = 0 if (dx != 0 or dy != 0) else 0.4
        cost = d_to_t + (0.85 / (d_to_o + 1)) * 3 + proximity_pen + stay_pen
        # Deterministic tie-break: prefer larger x then larger y then smaller dx/dy magnitude toward target direction
        if best_cost is None or cost < best_cost or (cost == best_cost and (nx > sx or (nx == sx and ny > sy))):
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]