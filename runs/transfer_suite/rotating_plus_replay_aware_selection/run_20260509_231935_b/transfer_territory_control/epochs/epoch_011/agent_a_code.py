def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obs = {tuple(p) for p in (observation.get("obstacles") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}
    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}

    ox_list = list(opp_set)
    if ox_list:
        cx = sum(x for x, _ in ox_list) / len(ox_list)
        cy = sum(y for _, y in ox_list) / len(ox_list)
    else:
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        val = 0.0

        if (nx, ny) in opp_set:
            val += 50.0
        if (nx, ny) in un_set:
            dist_to_center = abs(nx - cx) + abs(ny - cy)
            val += 20.0 - 0.25 * dist_to_center

        # Prefer growing your area while reducing opponent counterclaim leverage.
        if (nx, ny) in self_set:
            val += 5.0

        # Local safety: avoid moving next to opponent-owned cells unless we capture.
        adj_opp = 0
        adj_un = 0
        adj_own = 0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h:
                if (tx, ty) in opp_set:
                    adj_opp += 1
                elif (tx, ty) in un_set:
                    adj_un += 1
                elif (tx, ty) in self_set:
                    adj_own += 1

        if (nx, ny) in opp_set:
            val += 10.0 * adj_un + 2.0 * adj_own
            val -= 6.0 * adj_opp
        else:
            val += 6.0 * adj_un + 2.0 * adj_own
            val -= 10.0 * adj_opp

        # Tie-break deterministically toward increasing controlled cells region: center-ish from your position.
        val += -0.01 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        val += -0.001 * (abs(nx - sx) + abs(ny - sy))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]