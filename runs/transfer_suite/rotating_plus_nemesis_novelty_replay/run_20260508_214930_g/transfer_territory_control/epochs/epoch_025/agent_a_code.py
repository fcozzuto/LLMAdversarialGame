def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    def any_adj(nx, ny, sset):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    return True
        return False

    self_frontier = any_adj(sx, sy, opp_t)  # discourage sitting in duel zone
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        t = (nx, ny)

        if t in self_t:
            score = 2
        elif t in opp_t:
            score = 22 + 3 * adj_count(nx, ny, self_t) - 2 * adj_count(nx, ny, opp_t)
        elif t in unclaimed:
            score = 10 + 2 * adj_count(nx, ny, self_t) + 1 * adj_count(nx, ny, opp_t)
            if any_adj(nx, ny, opp_t):
                score -= 4  # avoid walking into opponent's counterclaim pressure
        else:
            score = 1  # unknown/unreachable-ish

        # Encourage progress towards center of unclaimed: bias by distance to nearest unclaimed cell.
        # Deterministic but cheap: sample a few nearest candidates.
        if unclaimed:
            # compute min manhattan distance using a small deterministic subset
            bestd = 10**9
            # take up to 6 lexicographically from unclaimed within a bounding heuristic
            # (sorted deterministically by coordinates)
            for k, (ux, uy) in enumerate(sorted(unclaimed)[:20]):
                d = abs(ux - nx) + abs(uy - ny)
                if d < bestd:
                    bestd = d
                if k >= 5 and bestd <= 2:
                    break
            score += 3 / (1 + bestd)

        # If on/near opponent frontier, prefer moves that increase self adjacency
        if self_frontier and adj_count(nx, ny, self_t) <= adj_count(sx, sy, self_t):
            score -= 2

        # Tie-break deterministically: prefer not-staying unless scores clearly better
        if (dx, dy) == (0, 0):
            score -= 0.15

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]