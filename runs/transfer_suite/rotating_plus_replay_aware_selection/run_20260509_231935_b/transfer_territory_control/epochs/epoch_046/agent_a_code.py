def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs9 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn = int(observation.get("turn_index", 0))
    dirs = dirs9[turn % 9:] + dirs9[:turn % 9]

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    frontier = set()
    for (x, y) in self_terr:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                t = (nx, ny)
                if t in unclaimed:
                    frontier.add(t)
    target_set = frontier if frontier else (unclaimed if unclaimed else opp_terr)
    if not target_set:
        return [0, 0]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        # Favor capturing unclaimed first; then pushing into opponent territory.
        cap = 0
        if cell in unclaimed:
            cap += 600
        elif cell in opp_terr:
            cap += 320
        elif cell in self_terr:
            cap += 120

        # Distance to nearest target in chosen target set.
        # Deterministic: scan targets in a deterministic order.
        mind = 10**9
        for tx, ty in sorted(target_set):
            d = abs(tx - nx) + abs(ty - ny)
            if d < mind:
                mind = d
                if mind == 0:
                    break
        dist_score = -5 * mind

        # Small bias to expand toward unclaimed (even if target_set is opp_terr).
        bias = 0
        if not frontier and unclaimed:
            for ux, uy in unclaimed:
                d = abs(ux - nx) + abs(uy - ny)
                if d <= 2:
                    bias += 40
                    break

        score = cap + dist_score + bias
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]