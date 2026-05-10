def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    ocx = w - 1
    ocy = h - 1
    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px
            sy += py
        ocx, ocy = sx / n, sy / n

    scores = observation.get("scores") or {}
    self_name = observation.get("self_name")
    opponent_name = observation.get("opponent_name")
    my_score = scores.get(self_name, 0)
    opp_score = scores.get(opponent_name, 0)
    lead = my_score > opp_score

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(px, py, target_set):
        c = 0
        for ddx, ddy in dirs:
            nx2, ny2 = px + ddx, py + ddy
            if (nx2, ny2) in target_set:
                c += 1
        return c

    best = (0, 0, -10**18)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            nx, ny = x, y  # deterministic: blocked -> stay
        cell = (nx, ny)

        d_to_opp = abs(nx - ocx) + abs(ny - ocy)
        d_bias = (d_to_opp if lead else -d_to_opp)

        frontier = adj_count(nx, ny, unclaimed)
        self_adj = adj_count(nx, ny, selfT)
        opp_here = cell in oppT
        unclaimed_here = cell in unclaimed
        self_here = cell in selfT

        score = 0
        if unclaimed_here:
            score += 50 + 6 * frontier + 3 * self_adj
        if opp_here:
            score += 28 + 3 * frontier + 2 * self_adj
        if self_here:
            score += 6 + 2 * self_adj

        # Prefer moves that keep our territory connected (if not already)
        if not self_adj and not self_here and selfT:
            score -= 12

        # Avoid dead-end expansion when staying doesn't help much
        if cell == (x, y):
            score -= 3 + 2 * frontier

        score += 1.5 * d_bias
        if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]