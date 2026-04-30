def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Main objective: move to a position that yields best "win margin" on some resource.
        if resources:
            local_best = -10**9
            for tx, ty in resources:
                d_me = cheb(nx, ny, tx, ty)
                d_op = cheb(ox, oy, tx, ty)
                # Prefer resource where we are closer than opponent (higher margin).
                margin = d_op - d_me
                # Minor preference: shorter absolute distance for tie-breaking.
                val = margin * 10 - d_me
                if val > local_best:
                    local_best = val
        else:
            # No resources left: just move to reduce distance to opponent.
            local_best = -cheb(nx, ny, ox, oy) * 10

        # Small shaping: keep near center and avoid walking into opponent too directly.
        center_pen = cheb(nx, ny, int(round(cx)), int(round(cy)))
        opp_prox = cheb(nx, ny, ox, oy)

        score = local_best - 0.3 * center_pen + 0.05 * opp_prox
        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            # Deterministic tie-break: prefer moves with smaller dx, then smaller dy magnitude.
            if (abs(dx), abs(dy), dx, dy) < (abs(best[0]), abs(best[1]), best[0], best[1]):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]