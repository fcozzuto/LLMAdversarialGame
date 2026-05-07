def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = sorted(moves, key=lambda t: (t[0], t[1]))

    opp_target = min(resources, key=lambda r: (md(ox, oy, r[0], r[1]), r[0], r[1]))
    best_score = -10**18
    best_move = (0, 0)

    # If we're not currently contesting (behind everywhere), deny by moving toward opponent's nearest resource.
    # Otherwise, race for a resource where we can arrive no later than opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        best_adv = -10**18
        best_sd_for_adv = 10**9
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_sd_for_adv):
                best_adv = adv
                best_sd_for_adv = sd

        if best_adv >= 0:
            # Race: prioritize being earlier, then being closer.
            opp_to_best = md(ox, oy, resources[0][0], resources[0][1])  # unused placeholder, kept out
            score = 1000 * best_adv - best_sd_for_adv
        else:
            # Deny: move toward opponent's nearest resource while still keeping options open.
            deny_dist = md(nx, ny, opp_target[0], opp_target[1])
            nearest_any = min(md(nx, ny, r[0], r[1]) for r in resources)
            score = -500 * deny_dist - nearest_any

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]