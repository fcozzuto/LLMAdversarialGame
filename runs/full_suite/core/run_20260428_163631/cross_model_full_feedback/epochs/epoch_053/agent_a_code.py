def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    my = (sx, sy)
    op = (ox, oy)

    # If resources are present, choose move that creates the biggest distance lead to a contested resource,
    # while discouraging stepping into opponent "reach" next turn.
    best = (-10**9, 0, 0, 0)
    for dx, dy, nx, ny in legal:
        score = 0
        my2 = (nx, ny)

        # discourage moving into/adjacent to opponent unless it yields a large lead
        opp_reach = cheb(my2, op)
        if opp_reach <= 1:
            score -= 2

        if resources:
            for r in resources:
                d_my = cheb(my2, r)
                d_op = cheb(op, r)
                # Prefer resources where we are closer than opponent would be (or at least reduce their lead).
                lead = d_op - d_my
                # Also lightly prefer closer actual progress.
                score += 3 * lead - 0.1 * d_my
            # Prefer staying aligned to the "front" of resources: maximize (opp_dist - my_dist) for nearest resource.
            nearest = None
            bestlead = -10**9
            for r in resources:
                lead = cheb(op, r) - cheb(my2, r)
                if lead > bestlead:
                    bestlead = lead
                    nearest = r
            score += 2 * bestlead
        else:
            # No resources: run away deterministically by maximizing distance to opponent.
            score = cheb(my2, op)

        # Deterministic tie-break: prefer smaller dx then smaller dy then lexicographic position.
        if (score, -dx, -dy, nx, ny) > best:
            best = (score, -dx, -dy, nx, ny)

    return [int(-best[1]), int(-best[2])]