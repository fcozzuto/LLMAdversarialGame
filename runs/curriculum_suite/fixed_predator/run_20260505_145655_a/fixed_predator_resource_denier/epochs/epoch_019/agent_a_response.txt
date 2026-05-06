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
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Prefer moving toward resources we can reach no worse than opponent, else deny their advantage.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        local_best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            cur_selfd = abs(sx - rx) + abs(sy - ry)
            cur_oppd = abs(ox - rx) + abs(oy - ry)

            # Advantage term; higher when we become closer than opponent.
            adv = (oppd - selfd)
            # Denial term: if opponent is currently closer, prioritize reducing that gap.
            deny = 0
            if cur_oppd < cur_selfd:
                deny = (cur_selfd - cur_oppd) - (selfd - oppd)  # positive if we improve denial

            # Small preference for shorter paths.
            val = adv * 6 - selfd * 1.2 + deny * 4
            if selfd == 0:
                val += 1000
            if oppd == 0:
                val -= 200

            if val > local_best:
                local_best = val

        if local_best > best_val:
            best_val = local_best
            best_move = [dx, dy]

    return best_move