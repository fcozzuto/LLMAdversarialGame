def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    unclaimed = observation.get("unclaimed_cells") or []
    opp_t = observation.get("opponent_territory") or []
    targets = (unclaimed + opp_t)[:64]
    if not targets:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    self_count = observation.get("self_territory_count", 0)
    opp_count = observation.get("opponent_territory_count", 0)
    behind = self_count <= opp_count

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_to = []
    for tx, ty in targets:
        dso = man(ox, oy, tx, ty)
        selfd = man(sx, sy, tx, ty)
        # If behind, prefer targets closer to us than opponent; otherwise prefer slowing opponent from them.
        score = (selfd - 0.35 * dso) if behind else (dso - 0.35 * selfd)
        opp_to.append((score, selfd, dso, tx, ty))
    opp_to.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4]))
    top = opp_to[:10]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate by best achievable target from this next position
        local_best = 10**18
        local_adv = -10**18
        for _, _, _, tx, ty in top:
            d_self = man(nx, ny, tx, ty)
            d_opp = man(ox, oy, tx, ty)
            # Encourage capturing nearby; if behind, strongly punish giving opponent an immediate closer race.
            race = (d_self - 0.15 * d_opp) if behind else (d_self + 0.15 * d_opp)
            if race < local_best:
                local_best = race
                local_adv = -race
        val = local_adv
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_val == -10**18:
        return [0, 0]
    return [best_move[0], best_move[1]]