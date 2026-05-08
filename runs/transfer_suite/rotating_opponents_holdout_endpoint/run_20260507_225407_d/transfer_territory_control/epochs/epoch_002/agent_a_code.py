def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    self_cells = observation.get("self_territory", []) or []
    opp_cells = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_count = observation.get("self_territory_count", len(self_cells))
    opp_count = observation.get("opponent_territory_count", len(opp_cells))
    behind = self_count < opp_count

    opp_set = set((x, y) for x, y in opp_cells)
    self_set = set((x, y) for x, y in self_cells)

    def inside(x, y):
        w = observation.get("grid_width", 8)
        h = observation.get("grid_height", 8)
        return 0 <= x < w and 0 <= y < h

    # Choose a target: attack nearest opponent territory if behind; else expand to nearest unclaimed
    tx, ty = ox, oy
    if behind and opp_set:
        bestd = 10**9
        for x, y in opp_set:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd or (d == bestd and (x, y) < (tx, ty)):
                bestd, tx, ty = d, x, y
    else:
        if unclaimed:
            bestd = 10**9
            for x, y in unclaimed:
                d = abs(x - sx) + abs(y - sy)
                if d < bestd or (d == bestd and (x, y) < (tx, ty)):
                    bestd, tx, ty = d, x, y
        elif opp_set:
            bestd = 10**9
            for x, y in opp_set:
                d = abs(x - sx) + abs(y - sy)
                if d < bestd or (d == bestd and (x, y) < (tx, ty)):
                    bestd, tx, ty = d, x, y
        else:
            tx, ty = (ox, oy)

    # If target is blocked by obstacles, bias toward an adjacent unblocked neighbor of target
    cand_targets = [(tx, ty)]
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
        nx, ny = tx + dx, ty + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cand_targets.append((nx, ny))

    # Deterministic move scoring with obstacle avoidance
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Base preference: reduce distance to chosen candidate target
        best_td = 10**9
        for atx, aty in cand_targets:
            d = abs(atx - nx) + abs(aty - ny)
            if d < best_td:
                best_td = d
        # Territory incentive: stepping into opponent territory flips control
        enters_opp = (nx, ny) in opp_set
        already_own = (nx, ny) in self_set
        # Encourage exploration slightly: prefer unclaimed when not behind
        enters_unclaimed = (nx, ny) in set(map(tuple, unclaimed)) if unclaimed else False

        score = -best_td
        if enters_opp:
            score += 50
        if already_own:
            score -= 1
        if enters_unclaimed and not behind:
            score += 5

        # Tie-break deterministically by move order
        if score > best_score or (score == best_score and (mdx, mdy) < best_move):
            best_score = score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]