def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacles_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles_set.add((p[0], p[1]))
    res_list = []
    res_set = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            t = (p[0], p[1])
            res_list.append(t)
            res_set.add(t)

    def legal_moves(x, y):
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles_set:
                    moves.append((dx, dy))
        return moves

    if (sx, sy) in res_set:
        return [0, 0]

    legal = legal_moves(sx, sy)
    if not legal:
        return [0, 0]
    if not res_list:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_key = None

    # Choose the move that maximizes our advantage to a contested resource:
    # key = (advantage, -our_dist, resource_dist_min_tiebreak)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        our_dist = 10**9
        opp_dist = 10**9
        best_adv = -10**9
        best_our_d = 10**9
        best_resource_d = 10**9

        for rx, ry in res_list:
            d1 = dist(nx, ny, rx, ry)
            d2 = dist(ox, oy, rx, ry)
            adv = d2 - d1  # larger => we are closer
            if (adv > best_adv) or (adv == best_adv and (d1 < best_our_d or (d1 == best_our_d and (d1 + d2) < best_resource_d))):
                best_adv = adv
                best_our_d = d1
                best_resource_d = d1 + d2
                our_dist = d1
                opp_dist = d2

        key = (best_adv, -best_our_d, best_resource_d, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]