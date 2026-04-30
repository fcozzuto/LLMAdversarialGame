def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    best = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Base: avoid getting closer to opponent too much unless it helps resources
        base = -0.15 * cheb(nx, ny, ox, oy)

        if resources:
            # Prefer moves where we become relatively closer to some resource than opponent.
            move_score = base
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Advantage: smaller my distance than opponent's
                adv = (opd - myd)
                # Small tie-break: prefer lower myd to reduce time-to-pick
                score = 2.0 * adv - 0.05 * myd
                if score > move_score:
                    move_score = score
            cand_score = move_score
        else:
            # No visible resources: drift to center while keeping distance from opponent.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = cheb(nx, ny, int(cx), int(cy))
            cand_score = base - 0.05 * dc

        # Deterministic tie-break: lexicographic on (dx,dy) to keep stable.
        if best is None or cand_score > best or (cand_score == best and (dx, dy) < best_move):
            best = cand_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]