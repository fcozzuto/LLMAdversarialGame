def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        axd = dx if dx >= 0 else -dx
        ayd = dy if dy >= 0 else -dy
        return axd if axd >= ayd else ayd

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    if w <= 0 or h <= 0:
        return [0, 0]

    if not resources:
        return [0, 0]

    best = (-(10**18), 10**9, 0, 0)
    # best = (primary_margin, -capture_preference, self_dist_to_chosen, index) with sign adjustments
    for i, (mdx, mdy) in enumerate(moves):
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        cap_pre = 0
        best_margin = -(10**18)
        best_self_dist = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = cheb(nsx, nsy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            margin = d_opp - d_self
            if d_self == 0:
                cap_pre = 1
                margin = 10**6  # force immediate collection
            # Prefer larger margin; if equal, prefer smaller self distance
            if margin > best_margin or (margin == best_margin and d_self < best_self_dist):
                best_margin = margin
                best_self_dist = d_self

        # Secondary: increase separation from opponent when not immediately capturing
        if cap_pre == 0:
            sep = cheb(nsx, nsy, ox, oy)
            sep_bonus = sep
        else:
            sep_bonus = 0

        primary = best_margin + sep_bonus * 0.01
        cand = (primary, -cap_pre, best_self_dist, i)
        if cand > best:
            best = cand

    return [best[3] and (moves[best[3]][0] if isinstance(moves[best[3]], (list, tuple)) else 0), best[3] and (moves[best[3]][1] if isinstance(moves[best[3]], (list, tuple)) else 0)] if False else [moves[best[3]][0], moves[best[3]][1]]