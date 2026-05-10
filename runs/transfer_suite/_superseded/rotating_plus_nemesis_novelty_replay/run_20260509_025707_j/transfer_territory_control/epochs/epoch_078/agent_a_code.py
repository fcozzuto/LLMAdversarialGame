def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    un_list = observation.get("unclaimed_cells") or []
    myc = observation.get("self_territory_count", len(my_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    yield x + dx, y + dy

    def near_opp(x, y):
        for nx, ny in neighbors(x, y):
            if (nx, ny) in opp_set:
                return True
        return False

    my_behind = myc <= opc
    mode_flip = (observation["turn_index"] % 10) < 5  # deterministic alternating pressure

    best = (None, -10**9)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    move_dirs = [((x, y), (x - sx, y - sy)) for x in range(sx - 1, sx + 2) for y in range(sy - 1, sy + 2) if inb(x, y)]
    for (tx, ty), (dx, dy) in move_dirs:
        if (tx, ty) in obstacles:
            continue
        if not inb(tx, ty):
            continue
        t = 0
        if (tx, ty) in opp_set:
            t += 5 if my_behind else 3
            t += 2 if near_opp(tx, ty) else 0
            if mode_flip:
                t += 1
        elif (tx, ty) in un_set:
            t += 3 if my_behind else 2
            if near_opp(tx, ty):
                t += 2
            if mode_flip:
                t += 1
        elif (tx, ty) in my_set:
            t += 0.2
            if near_opp(tx, ty):
                t += 1.2
        else:
            t -= 0.2

        t += 0.6 * (-(abs(tx - cx) + abs(ty - cy)))
        if un_list:
            md = 10**9
            for ux, uy in un_list:
                d = abs(ux - tx) + abs(uy - ty)
                if d < md:
                    md = d
            t += 1.6 / (1 + md)

        # Prefer not moving away from our territory too aggressively
        if my_set:
            mdm = 10**9
            for mx, my in my_set:
                d = abs(mx - tx) + abs(my - ty)
                if d < mdm:
                    mdm = d
            t += 1.0 / (1 + mdm)

        # Mild obstacle-avoidance
        for nx, ny in neighbors(tx, ty):
            if (nx, ny) in obstacles:
                t -= 0.3

        if t > best[1] or (t == best[1] and (dx, dy) == (0, 0)):
            best = ((tx, ty), t)
            best_move = [dx, dy]

    if best[0] is None:
        return [0, 0]
    return [best_move[0], best_move[1]]