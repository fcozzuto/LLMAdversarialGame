def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Primary: maximize advantage over opponent on contested resources.
        val = 0
        for tx, ty in resources:
            d_opp = cheb(ox, oy, tx, ty)
            d_self = cheb(nx, ny, tx, ty)
            adv = d_opp - d_self  # positive means we are closer after our move
            # Strongly value resources we can reach no later than opponent; also prefer near targets.
            if adv >= 0:
                val += 30 + adv * 5
            else:
                val += adv * 3 - (d_self + 1)

        # Secondary: slightly prefer moving toward the single best target (nearest we can contest).
        closest = None
        closest_d = 10**9
        for tx, ty in resources:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            if d_self <= d_opp:
                if d_self < closest_d:
                    closest_d = d_self
                    closest = (tx, ty)
        if closest is not None:
            val += 10 - closest_d
        else:
            # Otherwise, at least head toward globally nearest resource.
            val += 0.5 * (-(min(cheb(nx, ny, tx, ty) for tx, ty in resources)))

        if best is None or val > best_val:
            best_val = val
            best = (dxm, dym)
        elif val == best_val:
            # Deterministic tie-break: lexicographic smallest move.
            if (dxm, dym) < best:
                best = (dxm, dym)

    return [int(best[0]), int(best[1])]