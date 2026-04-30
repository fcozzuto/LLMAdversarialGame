def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose a resource we can reach earlier than opponent; otherwise fallback to best reachable, plus defensive spacing.
    best = None
    best_gap = -10**9
    for x, y in resources:
        md_s = cheb(sx, sy, x, y)
        md_o = cheb(ox, oy, x, y)
        gap = md_o - md_s  # positive means we are earlier
        if gap > best_gap or (gap == best_gap and (best is None or md_s < cheb(sx, sy, best[0], best[1]))):
            best_gap = gap
            best = (x, y)

    tx, ty = best if best is not None else (sx, sy)

    # Evaluate immediate move by: reduce distance to chosen target, and if contested, increase separation from opponent.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)

        md_s_now = cheb(sx, sy, tx, ty)
        md_o_now = cheb(ox, oy, tx, ty)
        contested = (md_s_now >= md_o_now)  # we aren't earlier

        d_o = cheb(nx, ny, ox, oy)
        score = -d_t * 10

        # If contested (opponent likely races), prioritize denying: move to increase distance from opponent.
        if contested:
            score += d_o * 3
        else:
            # If we lead, also lightly keep away from opponent to prevent steals.
            score += d_o * 1

        # Micro anti-block: prefer moves that are not adjacent to obstacles too tightly.
        adj_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in blocked:
                    adj_block += 1
        score -= adj_block * 0.2

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move