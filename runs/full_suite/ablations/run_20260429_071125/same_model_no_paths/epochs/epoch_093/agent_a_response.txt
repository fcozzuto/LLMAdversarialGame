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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, 10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if d < best[2]:
                best = (dx, dy, d)
        return [best[0], best[1]]

    # Target scoring: prioritize resources where we can get there earlier vs opponent.
    resources_sorted = sorted(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]) - cheb(ox, oy, t[0], t[1]),
                                                        cheb(sx, sy, t[0], t[1]), t[0], t[1]))
    # Consider only the top few targets for stability.
    candidates = resources_sorted[: min(5, len(resources_sorted))]

    # One-step action selection: minimize "opponent advantage" after the move, with obstacle-aware tie-break.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 10**18
        for tx, ty in candidates:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Lower is better: we want myd <= opd; also reduce myd to finish.
            local = (myd - opd) * 100 - myd
            # Also slightly penalize moves that step adjacent to obstacles (to avoid getting stuck).
            adj_pen = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    px, py = nx + ax, ny + ay
                    if (px, py) in obstacles:
                        adj_pen += 1
            local += adj_pen * 0.25
            if local < score:
                score = local
        # Deterministic tie-break: prefer closer to center, then lexicographic move.
        if best_score is None or score < best_score or (score == best_score and (cheb(nx, ny, (w-1)//2, (h-1)//2), dx, dy) < (cheb(sx+best_move[0], sy+best_move[1], (w-1)//2, (h-1)//2), best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]