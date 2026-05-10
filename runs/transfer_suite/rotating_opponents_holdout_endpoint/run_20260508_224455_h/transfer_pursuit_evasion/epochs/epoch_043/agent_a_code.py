def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "escape", "coward"))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Greedy one-step lookahead with deterministic tie-break
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # If evader, bias toward the corner farthest from pursuer; if pursuer, toward corner nearest opponent.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d_now = cheb(nx, ny, ox, oy)

        # Look one step ahead: assume opponent can respond optimally in the same direction (very rough).
        # Use the best possible change in distance after one move for a deterministic local evaluation.
        opp_best = None
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
                continue
            dd = cheb(nx, ny, tx, ty)
            if opp_best is None:
                opp_best = dd
            else:
                opp_best = max(opp_best, dd) if is_evader else min(opp_best, dd)

        if opp_best is None:
            opp_best = d_now

        if is_evader:
            # maximize distance; also move toward the farthest corner
            corner_bias = -cheb(nx, ny, far_corner[0], far_corner[1])
            score = opp_best * 10.0 + corner_bias
        else:
            # minimize distance; also move toward the near corner
            corner_bias = -cheb(nx, ny, near_corner[0], near_corner[1])
            score = -opp_best * 10.0 + corner_bias

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]