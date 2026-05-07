def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_list}

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = sorted(moves, key=lambda t: (t[0], t[1]))

    if not resources:
        return [0, 0]

    # Current contest status
    def best_adv_from(px, py):
        best = -10**9
        for rx, ry in resources:
            sd = md(px, py, rx, ry)
            od = md(ox, oy, rx, ry)
            a = od - sd
            if a > best:
                best = a
        return best

    curr_adv = best_adv_from(sx, sy)

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Evaluate this step by how much we can beat the opponent for any reachable resource
        best_adv = -10**9
        best_sd = 10**9
        best_od = 10**9
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            a = od - sd
            if a > best_adv or (a == best_adv and (sd < best_sd or (sd == best_sd and od < best_od))):
                best_adv, best_sd, best_od = a, sd, od

        # Strategy switch: if we're behind everywhere (curr_adv < 0), prioritize denial (maximize best_adv)
        # else prioritize winning races (maximize best_adv), with tie-break on closeness.
        if curr_adv < 0:
            val = (best_adv * 10000) - best_sd
        else:
            val = (best_adv * 10000) - best_sd - (0 if best_od > best_sd else 0.1 * best_od)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]