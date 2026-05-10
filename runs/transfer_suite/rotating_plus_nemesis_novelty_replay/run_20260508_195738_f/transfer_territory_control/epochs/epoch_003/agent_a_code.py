def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set((a[0], a[1]) for a in (observation.get("obstacles", []) or []))
    unclaimed = set((c[0], c[1]) for c in (observation.get("unclaimed_cells", []) or []))
    opp_cells = set((c[0], c[1]) for c in (observation.get("opponent_territory", []) or []))
    self_cells = set((c[0], c[1]) for c in (observation.get("self_territory", []) or []))

    def clamp_in(ax, ay):
        return 0 <= ax < w and 0 <= ay < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Precompute a couple nearest landmarks for speed/determinism
    nearest_unclaimed = None
    if unclaimed:
        nearest_unclaimed = min(unclaimed, key=lambda p: (cheb(x, y, p[0], p[1]), abs(p[0] - ox) + abs(p[1] - oy), p[0], p[1]))
    nearest_opp = None
    if opp_cells:
        nearest_opp = min(opp_cells, key=lambda p: (cheb(x, y, p[0], p[1]), p[0], p[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not clamp_in(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 8
        elif (nx, ny) in opp_cells:
            score += 9
        elif (nx, ny) in self_cells:
            score += 2
        else:
            score += 1

        # Frontier pressure: move toward either unclaimed or opponent territory depending on availability
        if nearest_unclaimed is not None:
            d = cheb(nx, ny, nearest_unclaimed[0], nearest_unclaimed[1])
            score += 6 - d
        if nearest_opp is not None:
            d2 = cheb(nx, ny, nearest_opp[0], nearest_opp[1])
            score += 4 - d2

        # Defensive tweak: avoid walking into the opponent if unclaimed targets exist
        if nearest_unclaimed is not None and (nx, ny) in opp_cells:
            score -= 2

        # Prefer reducing distance to opponent when we're close to claiming
        score += (3 - cheb(nx, ny, ox, oy)) * 0.5

        # Deterministic tie-break by move order then coordinates
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]