def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    if sx < 0 or sy < 0:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def near_opp(x, y):
        return any((x + dx, y + dy) in opp_set for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)

    def near_my(x, y):
        return any((x + dx, y + dy) in my_set for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)

    # pick a small deterministic target set from unclaimed
    un_list = list(un_set)
    if un_list:
        # prefer cells adjacent to opponent frontier, else edge, else closest to our position
        def key(c):
            x, y = c
            adj = 1 if near_opp(x, y) else 0
            edge = 1 if (x in (0, w - 1) or y in (0, h - 1)) else 0
            return (-adj, -edge, abs(x - sx) + abs(y - sy), x, y)
        un_list.sort(key=key)
        targets = un_list[:12]
    else:
        targets = []

    best = [0, 0]
    best_score = -10**9
    myc = observation.get("self_territory_count", len(my_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    attack = myc + 2 < opc  # when behind, press frontier more

    for dx, dy in moves:
        x, y = sx + dx, sy + dy
        if not inside(x, y) or (x, y) in obstacles:
            continue
        # base cell value
        score = 0
        if (x, y) in opp_set:
            score += 220 if attack else 160
        elif (x, y) in un_set:
            score += 140 if attack else 110
        elif (x, y) in my_set:
            score += 35
        else:
            score += 5

        # avoid walking into obstacle "corridors"
        obs_near = sum(1 for xx in (x - 1, x, x + 1) for yy in (y - 1, y, y + 1) if (xx, yy) in obstacles)
        score -= 12 * obs_near

        # frontier/expansion heuristic
        if targets:
            dmin = min(abs(tx - x) + abs(ty - y) for tx, ty in targets)
            score += 55 - 8 * dmin
            # if near opponent, weight more
            if near_opp(x, y):
                score += 30
        else:
            if near_opp(x, y):
                score += 35

        # keep somewhat connected (deterministic defense vs sweeper)
        if not near_my(x, y) and (x, y) not in opp_set:
            score -= 20

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best