def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = {tuple(p) for p in (observation.get("obstacles") or [])}
    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def score_cell(x, y):
        t = 0.0
        if (x, y) in self_set:
            t += 1.0
        elif (x, y) in opp_set:
            t += 9.0  # flipping enemy cell
        elif (x, y) in un_set:
            t += 6.0
        else:
            t += 2.0  # should be rare

        # Expansion / contest pressure around the destination
        own_adj = 0
        opp_adj = 0
        un_adj = 0
        for nx, ny in neigh8(x, y):
            if (nx, ny) in self_set:
                own_adj += 1
            elif (nx, ny) in opp_set:
                opp_adj += 1
            elif (nx, ny) in un_set:
                un_adj += 1

        t += 0.9 * own_adj
        t += 1.1 * un_adj
        t += 0.7 * opp_adj

        # Prefer making progress towards nearest enemy territory if we can contest it this move
        if opp_adj:
            # cheap deterministic "distance" estimate: Manhattan to nearest enemy using frontier-ish cells
            # (search not needed; approximate via min of dx/dy to any enemy neighbor if exists)
            t += 2.0

        # Slight penalty for moving away from our current area (encourage staying near)
        t -= 0.15 * (abs(x - sx) + abs(y - sy))

        return t

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = score_cell(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]