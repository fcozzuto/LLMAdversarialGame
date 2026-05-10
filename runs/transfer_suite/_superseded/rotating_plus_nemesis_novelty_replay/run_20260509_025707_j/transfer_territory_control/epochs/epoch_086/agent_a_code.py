def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(x, y) for x, y in (observation.get("obstacles") or [])}
    my_set = {(x, y) for x, y in (observation.get("self_territory") or [])}
    opp_set = {(x, y) for x, y in (observation.get("opponent_territory") or [])}
    un_set = {(x, y) for x, y in (observation.get("unclaimed_cells") or [])}
    myc = observation.get("self_territory_count", len(my_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    behind = myc < opc

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set:
                        return True
        return False

    def count_near_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        c += 1
        return c

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose a target type: if behind, capture cells that are adjacent to opponent frontier; else expand unclaimed near us.
    targets = []
    if behind:
        for x, y in un_set:
            if adj_opp(x, y):
                targets.append((x, y))
        if not targets:
            targets = list(un_set)
    else:
        for x, y in un_set:
            # Prefer edge-ish/near-center expansion while still being relatively safe
            if count_near_obst(x, y) <= 3:
                targets.append((x, y))
        if not targets:
            targets = list(un_set) if un_set else list(opp_set)

    tx, ty = (sx, sy)
    if targets:
        # Deterministic tie-breaking: fixed sort key
        def key(p):
            x, y = p
            return (abs(x - sx) + abs(y - sy), abs((x - (w - 1) / 2)) + abs((y - (h - 1) / 2)), x, y)
        tx, ty = sorted(targets, key=key)[0]

    best = (10**9, 0, 0)
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Score move: approach target; reward moving into opponent territory only when behind; penalize obstacles adjacency.
        dist = abs(nx - tx) + abs(ny - ty)
        in_opp = (nx, ny) in opp_set
        in_me = (nx, ny) in my_set
        flip_bonus = (2 if behind and in_opp else 0)
        claim_bonus = (1 if (nx, ny) in un_set else 0) + (0 if in_me else 0)
        obst_pen = count_near_obst(nx, ny)
        # Additional robustness: prefer not to step away from our bulk unless flipping
        bulk_ref = min(abs(nx - x) + abs(ny - y) for x, y in list(my_set)[:8]) if my_set else 0
        move_score = (dist - flip_bonus - claim_bonus) + obst_pen * 0.25 - (0.05 if bulk_ref == 0 else 0)
        k = (move_score, obst_pen, 0 if (dx, dy) == (0, 0) else 1)
        if k < best:
            best, best_move = k, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]