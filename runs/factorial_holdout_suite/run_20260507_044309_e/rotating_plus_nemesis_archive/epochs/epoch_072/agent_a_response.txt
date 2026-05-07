def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if inb(bx, by):
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Estimate: both try to minimize distance to the next available resource.
    my_best_opp = []
    opp_best = min(cheb(ox, oy, rx, ry) for rx, ry in resources)

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_best = min(cheb(nx, ny, rx, ry) for rx, ry in resources)

        # Race advantage: larger means we get closer sooner than opponent.
        score = (opp_best - my_best) * 100

        # Tie-break: favor moving toward a resource that is also "preferable"
        # (closer and not directly "behind" obstacles with respect to opponent).
        # Simple proxy: prefer resources with smaller cheb from our new pos, and
        # larger cheb from opponent to same resource.
        best_r = None
        best_r_val = None
        for rx, ry in resources:
            v = -cheb(nx, ny, rx, ry) + cheb(ox, oy, rx, ry)
            if best_r_val is None or v > best_r_val:
                best_r_val = v
                best_r = (rx, ry)
        rx, ry = best_r
        score += (cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry))

        # Avoid ending adjacent to no-win areas: small preference for staying in-bounds
        # already guaranteed; add mild preference for staying off center only when beneficial.
        score += 0

        # Deterministic tie-break: smallest (dx,dy) lexicographically by a fixed ordering.
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]