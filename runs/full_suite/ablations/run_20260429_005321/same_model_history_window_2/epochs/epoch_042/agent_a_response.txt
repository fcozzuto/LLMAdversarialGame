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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Fallback: drift toward center while avoiding obstacles.
        cx, cy = w // 2, h // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Strategy change: pick the immediate move that maximizes "steal pressure"
    # on the best available target (opponent advantage reduced while our advantage increased).
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        score_for_move = -cheb(nx, ny, ox, oy) * 0.2  # mild: don't let opponent crowd us
        # Evaluate best target for this move.
        local_best = -10**18
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            if myd == 0:
                local = 10**6  # landing on resource
            else:
                # primary: reduce opponent reach; secondary: make us closer
                local = (opd - myd) * 50 - myd * 3
                # penalty if we step adjacent to many obstacles (avoid traps)
                adj = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        if ax == 0 and ay == 0:
                            continue
                        x2, y2 = nx + ax, ny + ay
                        if 0 <= x2 < w and 0 <= y2 < h and (x2, y2) in obstacles:
                            adj += 1
                local -= adj * 2
            if local > local_best:
                local_best = local

        score_for_move += local_best
        if score_for_move > best_score or (score_for_move == best_score and (dx, dy) < best_move):
            best_score = score_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]