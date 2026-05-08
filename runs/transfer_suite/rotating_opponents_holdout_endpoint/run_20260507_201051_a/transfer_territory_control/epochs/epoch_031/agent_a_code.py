def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (observation.get("self_position") or [0, 0])[:2]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))
    st = set(map(tuple, observation.get("self_territory") or []))
    opp_pos = (observation.get("opponent_position") or [w - 1, h - 1])[:2]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Targeting: if unclaimed exist, aim for the ones closest to opponent; else aim at opponent centroid/pos.
    if unclaimed:
        cand = list(unclaimed)
        best = cand[0]
        if ot:
            ox = sum(x for x, y in ot) / len(ot)
            oy = sum(y for x, y in ot) / len(ot)
        else:
            ox, oy = opp_pos
        bestd = 10**9
        for x, y in cand:
            d = (abs(x - ox) + abs(y - oy)) * 3 + (abs(x - sx) + abs(y - sy))
            if d < bestd:
                bestd = d
                best = (x, y)
        tx, ty = best
    elif ot:
        tx = int(round(sum(x for x, y in ot) / len(ot)))
        ty = int(round(sum(y for x, y in ot) / len(ot)))
    else:
        tx, ty = opp_pos

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    best_tiebreak = (10**9, 10**9)

    # Precompute for "frontier pressure": count opponent-neighbor adjacency around candidate and current.
    def count_adj_opponent(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) in ot:
                c += 1
        return c

    cur_adj = count_adj_opponent(sx, sy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        # High value: flip opponent territory on entry.
        if (nx, ny) in ot:
            score += 18
        # Value: expand into unclaimed.
        if (nx, ny) in unclaimed:
            score += 6
        # Value: maintain growth by stepping near opponent frontier.
        adj = count_adj_opponent(nx, ny)
        score += 2 * (adj - cur_adj) + 1 * adj

        # Soft bias: move toward target (and thus likely frontier/unclaimed).
        dist = abs(nx - tx) + abs(ny - ty)
        score += 3 * (-dist)

        # Avoid "wasting" on own territory unless it improves frontier.
        if (nx, ny) in st:
            score -= 2
            score += 2 * max(0, adj)

        # Prefer not to stay if there's any positive gain.
        if dx == 0 and dy == 0:
            score -= 1

        # Tie-breakers: closer to target, then closer to opponent position.
        tiebreak = (dist, abs(nx - opp_pos[0]) + abs(ny - opp_pos[1]))
        if score > best_score or (score == best_score and tiebreak < best_tiebreak):
            best_score = score
            best_tiebreak = tiebreak
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]