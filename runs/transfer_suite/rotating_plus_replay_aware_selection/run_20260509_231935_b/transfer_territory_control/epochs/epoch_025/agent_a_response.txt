def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    if not unclaimed and not self_set and not opp_set:
        return [0, 0]

    # Targets: prefer unclaimed; if none, expand toward opponent territory; else just stay near own
    if unclaimed:
        targets = unclaimed
    elif opp_set:
        targets = list(opp_set)
    else:
        targets = list(self_set)

    def dist_to_targets(nx, ny):
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < best:
                best = d
        return best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue

        score = 0
        if (nx, ny) in self_set:
            score += 1.0
        elif (nx, ny) in opp_set:
            score += 2.3  # entering opponent territory flips on entry
        else:
            score += 1.2  # unclaimed or unknown -> likely expands

        dt = dist_to_targets(nx, ny)
        score += (1.0 / (1 + dt)) * 3.5  # prefer moves that get closer to targets

        # slight bias to keep spreading toward board center (reduces getting boxed-in)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= (abs(nx - cx) + abs(ny - cy)) * 0.02

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]