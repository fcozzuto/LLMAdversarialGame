def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(x), int(y)) for x, y in obstacles_list)
    ti = int(observation.get("turn_index", 0))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    rot = ti % len(moves)
    moves = moves[rot:] + moves[:rot]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obs_pen(x, y):
        p = 0
        for ex, ey in obstacles:
            d = abs(x - ex) + abs(y - ey)
            if d == 0:
                return 10**9
            if d == 1:
                p += 4
            elif d == 2:
                p += 1
        return p

    def best_resource_advantage(nx, ny):
        if not resources:
            return None
        my_best = -10**18
        for rx, ry in resources:
            my_d = dist_manh((nx, ny), (rx, ry))
            opp_d = dist_manh((ox, oy), (rx, ry))
            # prioritize resources where we are closer than opponent (opp_d - my_d larger)
            adv = opp_d - my_d
            # add mild preference to overall closeness for that resource
            adv -= 0.15 * my_d
            if adv > my_best:
                my_best = adv
        return my_best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adv = best_resource_advantage(nx, ny)
        if adv is None:
            # no resources: keep distance from opponent
            my_d_opp = dist_manh((nx, ny), (ox, oy))
            score = 2.0 * my_d_opp - obs_pen(nx, ny)
        else:
            # encourage moving toward a "winning" resource while discouraging risky near-obstacle steps
            my_d_opp = dist_manh((nx, ny), (ox, oy))
            # if opponent is near, slightly favor positions that reduce opponent's advantage
            opp_risk = 0.1 * (8 - min(8, my_d_opp))
            score = adv - opp_risk - obs_pen(nx, ny)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]