def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**30
    best_tie = -10**30  # prefer larger lead then closer

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        cur_val = 0
        cur_lead = -10**30
        cur_closest = 10**9

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            cur_closest = ds if ds < cur_closest else cur_closest
            lead = do - ds
            if lead > cur_lead:
                cur_lead = lead

            if ds == 0 and (nx, ny) == (rx, ry):
                val = 10**12
            else:
                val = lead * 1200 - ds * 3
                if do == 0 and (ox, oy) == (rx, ry):
                    val -= 5000  # don't step away from winning pickup race
            cur_val += val

        # Tie-break: maximize lead, then minimize our closest distance
        tie_val = cur_lead * 10**6 - cur_closest
        if cur_val > best_val or (cur_val == best_val and tie_val > best_tie):
            best_val = cur_val
            best_tie = tie_val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]