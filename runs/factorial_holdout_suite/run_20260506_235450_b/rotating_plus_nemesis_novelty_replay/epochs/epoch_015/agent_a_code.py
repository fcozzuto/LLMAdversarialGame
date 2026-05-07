def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def best_step(tgx, tgy):
        best = [0, 0]
        bestv = None
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer approaching target, avoid getting too close to opponent, and reduce opponent approach
            v = dist2(nx, ny, tgx, tgy) - 1.2 * dist2(nx, ny, ox, oy)
            if bestv is None or v < bestv:
                bestv = v
                best = [mx, my]
        return best

    if resources:
        # Choose a resource where we have a clearer advantage over opponent
        target = None
        best_score = None
        for rx, ry in resources:
            myd = dist2(sx, sy, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            adv = opd - myd  # positive means we're closer
            # Strongly prioritize decisive advantage; then prefer closer actual target
            s = (-adv, myd, rx, ry)
            if best_score is None or s < best_score:
                best_score = s
                target = (rx, ry)
        tx, ty = target
        move = best_step(tx, ty)
        return [int(move[0]), int(move[1])]

    # No resources: head to nearest corner (deterministic) but keep some distance from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = min(corners, key=lambda p: (dist2(sx, sy, p[0], p[1]) - 0.5 * dist2(p[0], p[1], ox, oy), p[0], p[1]))
    move = best_step(cx, cy)
    return [int(move[0]), int(move[1])]