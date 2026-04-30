def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    remaining = int(observation.get("remaining_resource_count", len(resources)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (0, 0); best_score = -10**18

    # If we are on a resource, stay (collection happens without moving)
    if (sx, sy) in set(resources):
        return [0, 0]

    res_set = set(resources)
    # Pre-rank resources by our closeness and by whether we can beat opponent there
    ranked = []
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Larger is better: being closer than opponent
        margin = d_opp - d_self
        ranked.append((margin, -d_self, rx, ry))
    ranked.sort(reverse=True)

    # Evaluate each move: best possible contested advantage after move
    # Prefer contesting the top few candidate resources deterministically.
    candidates = ranked[:min(6, len(ranked))]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # If move lands on a resource, strongly prefer it
        move_score = 0.0
        if (nx, ny) in res_set:
            return [dx, dy]

        # Strongly maximize contested advantage against a small set of resources
        local_best = -10**18
        for margin, neg_ds, rx, ry in candidates:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Encourage immediate advantage and longer-term reach toward same target
            # Tie-breakers are deterministic via ordering of candidates.
            score = (d_opp - d_self) * 1000.0 - d_self * 3.0 + (remaining * 0.05)
            # If we are currently far behind on this resource, deprioritize
            if d_opp - d_self < -1:
                score -= 200.0
            if score > local_best:
                local_best = score

        # Small additional preference: overall being closer to any resource
        any_d = 10**9
        for rx, ry in resources:
            any_d = min(any_d, cheb(nx, ny, rx, ry))
        local_best += -any_d * 0.2

        # Deterministic tie-break: prefer smaller dx^2+dy^2 then lexicographic
        tie = (dx*dx + dy*dy, dx, dy)
        cand = (local_best, -tie[0], -tie[1], -tie[2])
        best_tie = (best_score, 0, 0, 0)  # only for comparison structure
        if local_best > best_score:
            best_score = local_best
            best = (dx, dy)
        elif local_best == best_score:
            # compare tie deterministically
            if tie < (best[0]*best[0] + best[1]*best[1], best[0], best[1]):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]