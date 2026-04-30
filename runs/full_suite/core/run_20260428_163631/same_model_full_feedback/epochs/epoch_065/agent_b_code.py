def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = 0
            # Prefer resources where we are closer than opponent; also prefer nearer generally.
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Encourage captures: maximize (d_opp - d_self), penalize distance.
                score += (d_opp - d_self) * 10 - d_self
            # Additional small bias: avoid moving toward obstacles is already handled; bias toward center.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += -0.1 * cheb(nx, ny, int(cx + 0.5), int(cy + 0.5))
            if score > best_score:
                best_score = score
                best = (dx, dy)
    else:
        # No visible resources: move to increase distance from opponent and head to nearest corner-resource bias.
        target_x = 0 if sx > (w - 1) / 2.0 else w - 1
        target_y = 0 if sy > (h - 1) / 2.0 else h - 1
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_tgt = cheb(nx, ny, target_x, target_y)
            score = d_opp * 10 - d_tgt
            if score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]