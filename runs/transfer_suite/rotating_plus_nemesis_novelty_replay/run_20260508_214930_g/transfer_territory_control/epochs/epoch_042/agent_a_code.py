def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    best = (0, 0)
    best_score = -10**18
    base_dist_to_opp = abs(sx - ox) + abs(sy - oy)

    frontier = set()
    for (tx, ty) in self_t:
        for dx, dy in dirs:
            nx, ny = tx + dx, ty + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in unclaimed:
                frontier.add((nx, ny))

    target_set = frontier if frontier else unclaimed

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        score = 0

        # Immediate capture/contest
        if (nx, ny) in opp_t:
            score += 500
        if (nx, ny) in unclaimed:
            score += 60
        if (nx, ny) in self_t:
            score += 8

        # Directional pressure: reduce distance to opponent (while contesting)
        nd_opp = abs(nx - ox) + abs(ny - oy)
        score += (base_dist_to_opp - nd_opp) * 3

        # Prefer moving toward a nearby frontier/unclaimed cell deterministically
        if target_set:
            best_td = None
            for (tx, ty) in target_set:
                td = abs(tx - nx) + abs(ty - ny)
                if best_td is None or td < best_td or (td == best_td and (ty, tx) < best_tie):
                    best_td = td
                    best_tie = (ty, tx)
                    if best_td == 0:
                        break
            if best_td is not None:
                score += max(0, 25 - best_td)

        # Keep from wasting moves: slight penalty for stepping away from opponent distance too much
        score -= max(0, nd_opp - base_dist_to_opp) * 2

        # Gentle tie-break: prefer moves with smaller (dx,dy) lexicographically
        if score > best_score or (score == best_score and (ddx, ddy) < best):
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]