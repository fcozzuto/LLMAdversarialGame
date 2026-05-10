def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    myc = observation.get("self_territory_count", len(my_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    behind = (myc < opc)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count_opp(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set:
                        c += 1
        return c

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        val = 0.0
        if (nx, ny) in opp_set:
            val += 30.0 if behind else 18.0
        elif (nx, ny) in un_set:
            val += 10.0 if behind else 12.0
        elif (nx, ny) in my_set:
            val += 2.0
        else:
            val += 3.0

        val += 0.9 * adj_count_opp(nx, ny)

        dist_center_before = abs(sx - cx) + abs(sy - cy)
        dist_center_after = abs(nx - cx) + abs(ny - cy)
        val += (dist_center_before - dist_center_after) * (2.2 if not behind else 1.4)

        # If we're ahead, avoid walking into opponent territory unless it increases frontier contact.
        if (not behind) and (nx, ny) in opp_set:
            val -= 8.0 - 1.5 * adj_count_opp(nx, ny)

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]