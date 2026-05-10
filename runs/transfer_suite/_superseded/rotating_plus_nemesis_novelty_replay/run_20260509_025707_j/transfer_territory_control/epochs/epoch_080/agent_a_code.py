def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_terr = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_terr = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    move_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    yield x + dx, y + dy

    myc = observation.get("self_territory_count", len(my_terr))
    opc = observation.get("opponent_territory_count", len(opp_terr))
    behind = myc < opc

    # Targets: if behind, go to unclaimed cell that is adjacent to opponent to enable counter-flip; else expand near our frontier.
    opp_adj_un = []
    my_adj_un = []
    for (x, y) in unclaimed:
        if any((nx, ny) in opp_terr for nx, ny in neighbors(x, y)):
            opp_adj_un.append((x, y))
        if any((nx, ny) in my_terr for nx, ny in neighbors(x, y)):
            my_adj_un.append((x, y))

    if behind and opp_adj_un:
        targets = opp_adj_un
    else:
        targets = my_adj_un or list(unclaimed) or list(opp_terr)

    def score_cell(x, y):
        # Lower is better
        if not valid(x, y):
            return 10**9
        d = abs(x - sx) + abs(y - sy)
        near_opp = 0
        near_my = 0
        for nx, ny in neighbors(x, y):
            if (nx, ny) in opp_terr:
                near_opp += 1
            if (nx, ny) in my_terr:
                near_my += 1
        bonus = 0
        if behind:
            bonus -= 6 * (1 if (x, y) in opp_terr else 0)
            bonus -= 3 * near_opp
            bonus -= 2 if (x, y) in unclaimed else 0
        else:
            bonus -= 4 * near_my
            bonus -= 2 if (x, y) in unclaimed else 0
            bonus -= 1 * (1 if (x, y) in opp_terr else 0)
        # Prefer not getting boxed by obstacles
        obs_near = 0
        for nx, ny in neighbors(x, y):
            if (nx, ny) in obstacles:
                obs_near += 1
        bonus += 2 * obs_near
        return d + bonus

    # Choose next move that minimizes best reachable step score toward selected target set
    best = None
    best_dxdy = (0, 0)
    for dx, dy in move_dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate this step by looking at best target preference from the candidate destination
        if targets:
            val = min(score_cell(tx, ty) + abs(tx - nx) + abs(ty - ny) for tx, ty in targets)
        else:
            val = score_cell(nx, ny)
        if best is None or val < best or (val == best and (dx, dy) < best_dxdy):
            best = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]