def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    # Baseline: pick step that maximizes (opp_dist - my_dist) to the best resource,
    # with a small preference for reducing overall distance.
    best_score = -10**18
    best_move = [0, 0]

    # Deterministic ordering for equal scores
    resources_sorted = sorted(resources, key=lambda t: (t[0], t[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        # Evaluate best resource from this candidate next position
        # Prefer resources we can reach sooner than opponent; if opponent is already closer to everything,
        # then push toward the most contested resource denial (largest opp-my margin).
        local_best = -10**18
        local_best_tie = None
        for rx, ry in resources_sorted:
            myd = abs(rx - nx) + abs(ry - ny)
            opd = abs(rx - ox) + abs(ry - oy)
            # margin: positive means we are closer than opponent
            margin = opd - myd
            # If myd is 0, strong preference to collect immediately
            immediate = 10**6 if (nx == rx and ny == ry) else 0
            # Slightly encourage progress and discourage walking into corners when margins are equal
            progress = -myd
            # Weight margin heavily to handle resource denial opponent archetype
            score = immediate + margin * 1000 + progress
            if score > local_best or (score == local_best and (rx, ry) < local_best_tie):
                local_best = score
                local_best_tie = (rx, ry)

        if local_best > best_score or (local_best == best_score and (dx, dy) < tuple(best_move)):
            best_score = local_best
            best_move = [dx, dy]

    return best_move