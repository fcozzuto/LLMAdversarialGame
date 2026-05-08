def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break via move order.
    best = None
    best_score = None

    if is_evader:
        target_corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # Pick farthest corner (obstacles softly discourage landing adjacent to them).
        def corner_preference(cx, cy):
            d = cheb(ox, oy, cx, cy)
            pen = 0
            for nx, ny in ((cx, cy), (cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)):
                if (nx, ny) in obs:
                    pen += 1
            return d - 0.2 * pen

        target = max(target_corners, key=corner_preference)
        tx, ty = target
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Maximize distance from pursuer; also drift toward chosen corner.
            score = cheb(nx, ny, ox, oy) + 0.15 * cheb(nx, ny, tx, ty)
            if best_score is None or score > best_score:
                best_score, best = score, (dx, dy)
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Minimize distance to evader; prefer stepping with lower "escape potential" (closer to opponent).
            score = cheb(nx, ny, ox, oy)
            if best_score is None or score < best_score:
                best_score, best = score, (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]