def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    res_list = [(r[0], r[1]) for r in resources]
    res_set = set(res_list)

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    center_x, center_y = (W - 1) / 2.0, (H - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**30

    if not res_list:
        # No resources visible: drift to keep optional reachability
        tx, ty = int(round(center_x)), int(round(center_y))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            # prefer reducing distance to center
            score = -manh(nx, ny, tx, ty)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose a few closest resources to evaluate precisely (deterministic ordering)
    scored = []
    for rx, ry in res_list:
        d = manh(sx, sy, rx, ry)
        scored.append((d, rx, ry))
    scored.sort()
    top = scored[: min(4, len(scored))]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        # Immediate pickup advantage
        score = 0
        if (nx, ny) in res_set:
            score += 10**6

        # Main objective: get closer to resources first, prevent opponent from being closer
        # Use capped sum over top candidates; include opponent distance differential.
        for d0, rx, ry in top:
            our_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            # Encourage stealing races: higher when we become much closer than opponent
            race = (opp_d - our_d)
            # Encourage overall progress toward resources (our_d small)
            prog = -our_d
            score += 60 * race + 12 * prog - 3 * (our_d == 0)  # small stability penalty
            # Extra: avoid getting trapped by moving away from the best current resource
            if (rx, ry) == (top[0][1], top[0][2]):
                score += 10 * (top[0][0] - our_d)

        # Tie-break: keep toward center to reduce worst-case wandering
        score += -0.5 * (manh(nx, ny, center_x, center_y))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]