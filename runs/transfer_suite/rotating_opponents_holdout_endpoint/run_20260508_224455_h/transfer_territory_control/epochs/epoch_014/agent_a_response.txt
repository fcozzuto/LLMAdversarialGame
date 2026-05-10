def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    un_list = list(unclaimed)
    target_list = un_list if un_list else list(opp_t) if opp_t else []
    if not target_list:
        return [0, 0]

    def min_dist_to_targets(x, y, targets):
        md = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < md:
                md = d
        return md

    # Prefer unclaimed; if none, expand toward opponent-owned cells.
    targets = target_list
    go_unclaimed = bool(un_list)

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_t:
            score += 6
        elif (nx, ny) in unclaimed:
            score += 250 if go_unclaimed else 120
        elif (nx, ny) in opp_t:
            score -= 260 if go_unclaimed else 160

        # Frontier bonus (adjacent unclaimed)
        frontier = 0
        if unclaimed:
            for ddx, ddy in neigh8:
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in unclaimed:
                    frontier += 1
        score += frontier * (38 if go_unclaimed else 20)

        # Distance pressure toward the chosen target set
        d = min_dist_to_targets(nx, ny, targets)
        score -= d * (3 if go_unclaimed else 2)

        # Avoid staying still unless it is relatively good
        if dx == 0 and dy == 0:
            score -= 10

        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: prefer moves that reduce distance first, then lexicographically
            curd = min_dist_to_targets(nx, ny, targets)
            bdx, bdy = best
            bx, by = sx + bdx, sy + bdy
            bd = min_dist_to_targets(bx, by, targets)
            if curd < bd or (curd == bd and (dx, dy) < best):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]