def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Pick a denial target: the resource the opponent is currently closest to (or tied).
    best_opp_res = resources[0]
    best_opp_d = abs(ox - best_opp_res[0]) + abs(oy - best_opp_res[1])
    for rx, ry in resources[1:]:
        d = abs(ox - rx) + abs(oy - ry)
        if d < best_opp_d:
            best_opp_d = d
            best_opp_res = (rx, ry)

    tx, ty = best_opp_res

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Main objective: pick the resource we can out-approach; otherwise still steer toward denial target.
        local_best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            # Big reward if we are closer; small bias toward faster approach and slight preference to far-away opponent resources.
            sc = (oppd - selfd) * 8 - selfd
            if (rx, ry) == (tx, ty):
                sc += 6  # keep pressure on opponent's likely target
            if sc > local_best:
                local_best = sc

        # Secondary objective: move to reduce opponent's distance to their chosen resource (denial).
        denial = (best_opp_d - (abs(ox - tx) + abs(oy - ty)))  # currently 0; keep structure
        denial2 = (abs(ox - tx) + abs(oy - ty)) - (abs(nx - tx) + abs(ny - ty))
        # Encourage moving closer to denial target even if it isn't best_approach.
        sc_total = local_best + denial + denial2 * 2 - (abs(nx - tx) + abs(ny - ty)) * 0.15

        if sc_total > best_score:
            best_score = sc_total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]