def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def best_for(px, py):
        best = None
        for x, y in resources:
            d = cheb(px, py, x, y)
            if best is None or d < best[0]:
                best = (d, x, y)
        return best

    near_op = best_for(ox, oy)
    pred_tx, pred_ty = (ox, oy) if not near_op else (near_op[1], near_op[2])

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if pred_tx == ox and pred_ty == oy:
                score = cheb(nx, ny, sx, sy)
            else:
                # Intercept: move to reduce distance to opponent's likely next target,
                # but also avoid letting opponent get substantially closer to that target.
                d_to_op_target = cheb(nx, ny, pred_tx, pred_ty)
                d_op_to_target = cheb(ox, oy, pred_tx, pred_ty)
                # Find a nearby alternative that we can reach quickly to diversify.
                alt_pen = 0
                if resources:
                    alt = best_for(nx, ny)
                    alt_pen = alt[0] if alt else 0
                score = d_to_op_target + 0.65 * alt_pen + 0.35 * (d_op_to_target - cheb(nx, ny, pred_tx, pred_ty))
            # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
            key = (score, abs(dx), abs(dy), 0 if (dx == 0 and dy == 0) else 1)
            if best is None or key < best[0]:
                best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]