def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    myc = observation.get("self_territory_count", len(my_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    behind = myc < opc

    opp_list = list(opp_set)
    un_list = list(unclaimed)

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        return (dx if dx >= 0 else -dx) if (dx if dx >= 0 else -dx) > (dy if dy >= 0 else -dy) else (dy if dy >= 0 else -dy)

    # If we can flip immediately, do it.
    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        on_opp = (nx, ny) in opp_set
        if on_opp:
            score += 200 + (50 if behind else 0)
        # Prefer moving adjacent to opponent territory to force flips next turn.
        adj = False
        if not on_opp:
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    if (nx + adx, ny + ady) in opp_set:
                        adj = True
                        break
                if adj:
                    break
            if adj:
                score += 35 + (20 if behind else 0)
        # Distance shaping toward opponent when behind; otherwise toward unclaimed.
        if opp_list:
            score -= (10 if behind else 6) * cheb((nx, ny), (opp_list[0][0], opp_list[0][1]))
            # refine with nearest opponent
            mind = 10**9
            for p in opp_list:
                d = cheb((nx, ny), p)
                if d < mind:
                    mind = d
            score -= (12 if behind else 8) * mind
        if (not opp_list) and un_list:
            mind = 10**9
            for p in un_list:
                d = cheb((nx, ny), p)
                if d < mind:
                    mind = d
            score -= 6 * mind
        # Mild preference for unclaimed when it doesn't allow easy counter-flip
        if (nx, ny) in unclaimed and not on_opp:
            score += 10
        if score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score and best is not None:
            # deterministic tie-break: prefer smaller |dx|+|dy|, then dx, then dy
            if (abs(dx) + abs(dy), dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1]):
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]