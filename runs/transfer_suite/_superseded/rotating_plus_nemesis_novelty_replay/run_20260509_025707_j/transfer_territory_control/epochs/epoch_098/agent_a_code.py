def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    myc = observation.get("self_territory_count", len(my_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    move_list = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh_has(x, y, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in s:
                        return True
        return False

    def manhattan_to(x, y, targets):
        if not targets:
            return 999
        best = 999
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    behind = myc < opc
    opp_front = [(x, y) for (x, y) in un_set if neigh_has(x, y, opp_set)]
    my_front = [(x, y) for (x, y) in un_set if neigh_has(x, y, my_set)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        is_opp = (nx, ny) in opp_set
        is_un = (nx, ny) in un_set
        is_my = (nx, ny) in my_set
        opp_adj = neigh_has(nx, ny, opp_set)
        my_adj = neigh_has(nx, ny, my_set)

        score = 0
        if behind:
            score += 1400 if is_opp else 0
            score += 500 if (is_un and opp_adj) else 0
            score += 120 if opp_adj else 0
            score += 40 if my_adj and is_my else 0
            score -= 18 if (nx == sx and ny == sy) else 0
            score -= manhattan_to(nx, ny, opp_front[:8]) * 6
            score += 2 * (nx - sx) + 1 * (ny - sy)
        else:
            score += 220 if (is_un and my_adj) else 0
            score += 90 if my_adj else 0
            score += 20 if is_my else 0
            score -= 140 if opp_adj and not is_my else 0
            score += 3 if (nx == sx or ny == sy) else 0
            score -= manhattan_to(nx, ny, my_front[:8]) * 5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]