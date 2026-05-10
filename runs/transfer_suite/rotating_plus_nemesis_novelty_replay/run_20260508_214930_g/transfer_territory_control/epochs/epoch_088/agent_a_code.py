def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    turn = observation.get("turn_index", 0)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If we have more territory, prioritize safe expansion; else be more aggressive.
    myc = observation.get("self_territory_count", len(self_t))
    opc = observation.get("opponent_territory_count", len(opp_t))
    ahead = myc - opc

    # Estimate "frontier" around our territory using only local candidate moves.
    # Prefer stepping onto cells adjacent to our territory that are unclaimed/opp.
    best = (0, 0)
    best_score = -10**18
    base_dist = abs(sx - ox) + abs(sy - oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 600  # flipping on entry is strong
        elif (nx, ny) in unclaimed:
            score += 140
        elif (nx, ny) in self_t:
            score += 20
        else:
            score += 5

        # Encourage expanding away from opponent when ahead; chase when behind.
        nd = abs(nx - ox) + abs(ny - oy)
        if ahead >= 0:
            score += (nd - base_dist) * 6
        else:
            score += (base_dist - nd) * 7

        # Frontier adjacency: if candidate touches our territory, it's likely a safer/cleaner expansion.
        adj = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in self_t:
                adj += 1
        score += adj * (18 if (nx, ny) in unclaimed else 8)

        # Avoid stepping into opponent territory too many steps away from them unless aggressive turn.
        if (nx, ny) in opp_t:
            score += (1 if nd <= 3 else -2) * (25 if ahead < 0 else 10)

        # Mild turn-based bias to reduce dithering
        if turn % 2 == 0:
            score += (nx - sx) * 2 + (ny - sy) * 1
        else:
            score += (ny - sy) * 2 + (nx - sx) * 1

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]