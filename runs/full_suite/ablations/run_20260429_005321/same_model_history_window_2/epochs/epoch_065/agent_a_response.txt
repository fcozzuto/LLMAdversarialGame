def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Resource value: prefer where we are competitive vs opponent
    # Higher value = worse; we minimize.
    def best_value(px, py):
        if not resources:
            return cheb(px, py, ox, oy)  # otherwise just drift away from opponent when no targets
        best = 10**9
        for tx, ty in resources:
            myd = cheb(px, py, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # If opponent is closer, strongly avoid. If we are closer/equal, go.
            v = 10 * (myd - opd)
            # Also prefer absolute closeness
            v += myd
            # If myd==0 (standing on resource), prioritize
            if myd == 0:
                v = -10**6
            # Tie-break stable
            if v < best or (v == best and (ty, tx) < (best_ty, best_tx)):
                best = v
        return best

    # Deterministic tie-break bookkeeping
    best_move = (0, 0)
    best_score = 10**9
    # If resources exist, also add a mild "keep distance" when very close to opponent to avoid getting trapped
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = best_value(nx, ny)
        if resources and cheb(nx, ny, ox, oy) <= 1:
            score -= 1  # prefer slightly separating when competing
        if score < best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # stable lexicographic tie-break
            if (dy, dx) < (best_move[1], best_move[0]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]