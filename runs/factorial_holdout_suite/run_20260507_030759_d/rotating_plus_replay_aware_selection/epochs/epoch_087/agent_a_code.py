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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        axd = dx if dx >= 0 else -dx
        ayd = dy if dy >= 0 else -dy
        return axd if axd > ayd else ayd

    if w <= 0 or h <= 0:
        return [0, 0]

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                res_set.add((rx, ry))
    resources = list(res_set)

    # If no resources, drift away from opponent deterministically.
    if not resources:
        dx = 0 if sx == ox else (1 if ox < sx else -1)
        dy = 0 if sy == oy else (1 if oy < sy else -1)
        step = (1 if dx > 0 else -1 if dx < 0 else 0, 1 if dy > 0 else -1 if dy < 0 else 0)
        cand = (step[0], 0) if step[0] != 0 else (0, step[1])
        nx, ny = sx + cand[0], sy + cand[1]
        return [cand[0] if inb(nx, ny) else 0, cand[1] if inb(nx, ny) else 0]

    # Staying still only if currently on a resource.
    if (sx, sy) in res_set:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic tie-breaking: sort by value then by move preference list order.
    pref_idx = {m: i for i, m in enumerate(moves)}

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        # Evaluate this move by the most favorable resource we can reach first (or at least deny).
        val = -10**18
        for rx, ry in resources:
            d_own = cheb(nsx, nsy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Encourage being strictly closer; if not possible, prefer reducing opponent advantage.
            # Also reward closer proximity overall to avoid dithering.
            rel = d_opp - d_own
            score = rel * 20 - d_own
            if rel <= 0:
                score = rel * 35 - 2 * d_own  # stronger denial pressure when opponent is ahead
            # Small deterministic preference for resources nearer to center to reduce oscillation.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            cent = -0.05 * (abs(rx - cx) + abs(ry - cy))
            score += cent
            if score > val:
                val = score

        # If we choose a move that keeps us in the same cell due to obstacles, it would be invalid, already filtered.
        if val > best_val or (val == best_val and pref_idx[(mdx, mdy)] < pref_idx[best_move]):
            best_val = val
            best_move = (mdx, mdy)

    return [best_move[0], best_move[1]]