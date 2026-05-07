def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    # Aim to secure resources where we gain over the opponent, else approach closest.
    # Secondary bias: reduce opponent's ability by increasing their distance to those resources.
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        best_adv = -10**18
        best_heat = -10**18
        min_ds = 10**9
        for rx, ry in resources:
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            adv = do - ds  # positive means we are closer than opponent
            if adv > best_adv:
                best_adv = adv
                best_heat = do - ds * 0.3
            elif adv == best_adv:
                best_heat = max(best_heat, do - ds * 0.3)
            if ds < min_ds:
                min_ds = ds

        # If we have any advantage, maximize it; otherwise minimize our distance.
        score = 0
        if best_adv > 0:
            score = best_adv * 1000 + best_heat
        else:
            # Also mildly prefer moving toward resources that are currently "favorable" for us (closer than opponent).
            # Without advantage, this still differentiates moves.
            closest_do = 10**9
            for rx, ry in resources:
                do = abs(rx - ox) + abs(ry - oy)
                ds = abs(rx - nx) + abs(ry - ny)
                if do - ds >= best_adv:
                    if do < closest_do:
                        closest_do = do
            score = (-min_ds) * 100 - (closest_do * 0.01)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]