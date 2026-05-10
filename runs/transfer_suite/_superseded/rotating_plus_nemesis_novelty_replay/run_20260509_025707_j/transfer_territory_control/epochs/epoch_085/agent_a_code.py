def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    move_list = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def near_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    xx, yy = x + dx, y + dy
                    if (xx, yy) in obstacles:
                        c += 1
        return c

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set:
                        return True
        return False

    # If ahead, prioritize claiming unclaimed; if behind, attack opponent frontier more.
    behind = observation.get("self_territory_count", len(my_set)) <= observation.get("opponent_territory_count", len(opp_set))

    best = None
    best_val = -10**9
    t = observation.get("turn_index", 0)

    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            val = 80
            if behind:
                val += 20
            if adj_opp(nx, ny):
                val += 10
        elif (nx, ny) in un_set:
            val = 45
            if not behind and (t % 2 == 0):
                val += 8
            if adj_opp(nx, ny):
                val += 6
        elif (nx, ny) in my_set:
            val = 8
            if adj_opp(nx, ny):
                val += 12
        else:
            val = 2

        val += 2 * (1 if (nx, ny) in un_set else 0)
        val -= 3 * near_count(nx, ny)
        val -= 0.2 * (abs(nx - 3.5) + abs(ny - 3.5))  # mild center bias for stability

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]