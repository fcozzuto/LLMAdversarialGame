def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}
    resources = observation.get("resources") or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = [0, 0]
    best_val = -10**18

    if not resources:
        # Go toward opponent's furthest-along diagonal: reduce distance while avoiding obstacles.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            val = -md(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    # Resource race/denial heuristic: prefer moves that create the largest closeness advantage.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        best_adv = -10**9
        best_self_d = 10**9
        best_opp_d = 10**9
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and (self_d < best_self_d or (self_d == best_self_d and opp_d > best_opp_d))):
                best_adv, best_self_d, best_opp_d = adv, self_d, opp_d
        # If we can beat the opponent (adv>0), prioritize that strongly; otherwise still reduce self distance.
        val = best_adv * 100 - best_self_d + (best_opp_d - best_self_d) * 2
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move