def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    turns_remaining = observation.get("turns_remaining", 0)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # approximate opponent best distance in one move (ignoring our move)
    def opp_best_next_dist(rx, ry):
        best = 10**9
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if ok(nx, ny):
                d = dist(nx, ny, rx, ry)
                if d < best:
                    best = d
        return best if best != 10**9 else dist(ox, oy, rx, ry)

    best_move = [0, 0]
    best_val = -10**18
    # small deterministic ordering preference (bias ties)
    order_bias = {(0, 0): 0, (1, 1): 1, (-1, -1): 1, (1, -1): 2, (-1, 1): 2, (1, 0): 3, (-1, 0): 3, (0, 1): 4, (0, -1): 4}

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_best = -10**18
        # Prefer targets where we gain distance lead after our move, while not letting opponent steal instantly.
        for r in resources:
            rx, ry = r[0], r[1]
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            lead = opp_d - my_d  # positive means we are closer now/after our move

            opp_next = opp_best_next_dist(rx, ry)
            opp_immediate = 1 if opp_next <= 1 else 0  # likely contest soon

            # urgency: when time runs out, prioritize immediate collection/lead more
            urgency = 4 if turns_remaining <= 6 else (2 if turns_remaining <= 14 else 1)

            val = (lead * (12 + urgency)) - my_d * 1.5 - opp_immediate * (7 + urgency) - (0 if lead > 0 else abs(lead) * 2.0)
            # Strongly prefer immediate pickup cell
            if my_d == 0:
                val += 1000
            if val > my_best:
                my_best = val

        if my_best > best_val:
            best_val = my_best
            best_move = [dx, dy]
        elif my_best == best_val:
            if order_bias.get((dx, dy), 99) < order_bias.get((best_move[0], best_move[1]), 99):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]