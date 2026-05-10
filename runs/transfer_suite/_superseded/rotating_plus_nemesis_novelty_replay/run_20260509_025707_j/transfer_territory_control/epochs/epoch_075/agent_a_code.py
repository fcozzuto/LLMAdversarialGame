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
    if sx < 0 or sy < 0:
        return [0, 0]

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set:
                        return True
        return False

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def count_near_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        c += 1
        return c

    # Strategy shift: attack opponent frontier when behind; otherwise secure/expand unclaimed near our cells.
    attack = myc <= opc

    best = None
    bestv = -10**9
    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        v = 0.0
        if (nx, ny) in opp_set:
            v += 5.5 if attack else 4.2
        elif (nx, ny) in un_set:
            v += 3.8 if attack else 4.6
        elif (nx, ny) in my_set:
            v += 1.0
        else:
            v += 0.3
        if adj_opp(nx, ny):
            v += 1.2 if attack else 0.7
        v -= 0.55 * count_near_obst(nx, ny)
        # Tie-breaker: reduce distance to opponent territory when attacking; otherwise increase distance from opponent
        if attack and opp_set:
            ox, oy = min(opp_set, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            v -= 0.08 * (abs(ox - nx) + abs(oy - ny))
        elif (not attack) and opp_set:
            ox, oy = max(opp_set, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            v += 0.03 * (abs(ox - nx) + abs(oy - ny))
        # Deterministic preference order if values tie
        if v > bestv or (v == bestv and best is not None and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [0, 0] if best is None else [best[0], best[1]]