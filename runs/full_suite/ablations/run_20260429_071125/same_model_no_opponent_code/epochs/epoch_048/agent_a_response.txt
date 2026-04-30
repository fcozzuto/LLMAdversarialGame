def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [7, 7])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                res.append((x, y))

    if not res:
        # Fallback: move away from opponent if possible, else toward open space
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            score = d
            if score > best[1]:
                best = ((dx, dy), score)
        dx, dy = best[0] if best[0] else (0, 0)
        return [int(dx), int(dy)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose moves that secure resources where we are closer than opponent.
        # Score combines self progress and advantage over opponent; also mildly avoids opponent.
        score = 0
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Advantage: positive when we are closer than opponent
            adv = do - ds  # in [-7,7] range typically
            # Prefer states nearer to some resource, strongly when we can beat opponent.
            base = -ds
            # Boost securing when advantage is non-negative; penalize when we trail.
            if adv >= 0:
                base += 3.0 * adv
            else:
                base += 1.5 * adv

            score += base

        # Small repulsion from opponent to reduce collisions/contesting
        score -= 0.15 * cheb(nx, ny, ox, oy)

        # Deterministic tie-break: keep first best in move order
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]