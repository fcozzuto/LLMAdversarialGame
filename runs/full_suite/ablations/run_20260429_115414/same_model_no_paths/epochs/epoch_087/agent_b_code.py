def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        # Escape toward center when no resources are visible
        tx, ty = w // 2, h // 2
    else:
        # Pick a resource that we can reach earlier; otherwise contest the closest one
        # Deterministic tie-breaking by coordinates.
        best = None
        best_score = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do_ = cheb(ox, oy, rx, ry)
            # If opponent can reach sooner or equal, heavily penalize but still consider nearest contest.
            lead = do_ - ds
            score = 10_000 * lead - 5 * ds + 2 * (w + h - cheb(ox, oy, rx, ry))
            score -= 3 * (ds == 0)  # being on a resource not usually possible, but keep stable
            if best is None or score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score
                best = (rx, ry)
        tx, ty = best

    # Move one step toward target, but avoid easy opponent grabs.
    opp_near = cheb(sx, sy, ox, oy) <= 2
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(ox, oy, tx, ty)
        # Whether this move helps us beat opponent's reach
        improve = (dopp - dself)
        val = 2000 * improve - 6 * dself
        # Prefer progressing (lower distance to target)
        val += 3 * (cheb(sx, sy, tx, ty) - dself)
        # If opponent is close, avoid stepping adjacent to them unless it advances heavily
        if opp_near and cheb(nx, ny, ox, oy) <= 1:
            val -= 800
        # Avoid moving onto squares that are "behind" opponent relative to target (simple directional block)
        # Compare Chebyshev distance after move to opponent-target.
        if resources:
            if cheb(nx, ny, ox, oy) < 2 and cheb(nx, ny, tx, ty) >= cheb(sx, sy, tx, ty):
                val -= 200

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]