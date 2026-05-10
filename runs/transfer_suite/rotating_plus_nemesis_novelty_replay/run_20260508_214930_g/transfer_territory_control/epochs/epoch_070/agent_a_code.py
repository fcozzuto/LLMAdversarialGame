def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    kdirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    base_to_opp = abs(sx - ox) + abs(sy - oy)
    base_to_opp_t = min((abs(sx - tx) + abs(sy - ty) for (tx, ty) in opp_t), default=10**9)

    best = [0, 0]
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        score = 0

        if (nx, ny) in opp_t:
            score += 1200
        elif (nx, ny) in unclaimed:
            score += 120
        elif (nx, ny) in self_t:
            score += 20

        nd_opp = abs(nx - ox) + abs(ny - oy)
        score += (base_to_opp - nd_opp) * 6

        nd_opp_t = min((abs(nx - tx) + abs(ny - ty) for (tx, ty) in opp_t), default=10**9)
        if opp_t:
            score += (base_to_opp_t - nd_opp_t) * 10

        nb_opp = 0
        nb_unc = 0
        nb_self = 0
        for ddx2, ddy2 in kdirs:
            px, py = nx + ddx2, ny + ddy2
            if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                if (px, py) in opp_t:
                    nb_opp += 1
                elif (px, py) in unclaimed:
                    nb_unc += 1
                elif (px, py) in self_t:
                    nb_self += 1
        score += nb_opp * 45
        score += nb_unc * 10
        score += nb_self * 3

        if nd_opp_t == 0 and (nx, ny) in opp_t:
            score += 200

        if score > best_score:
            best_score = score
            best = [ddx, ddy]

    return best