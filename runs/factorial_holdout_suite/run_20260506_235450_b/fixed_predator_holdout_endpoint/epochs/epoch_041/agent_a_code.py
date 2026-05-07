def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res = [(int(r[0]), int(r[1])) for r in resources]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Focus on the closest few resources; combine "race advantage" and "near-term capture"
    res_sorted = sorted(res, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    top = res_sorted[:3] if len(res_sorted) >= 3 else res_sorted

    best = (None, -10**18)
    for dx, dy, nx, ny in legal:
        score = 0
        for rx, ry in top:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)

            if sd == 0:
                score += 1000000
                continue

            # Advantage: positive if we are closer than opponent
            adv = od - sd
            if od <= sd:
                # If opponent can grab at least as fast, strongly discourage
                score -= (5000 - min(5000, 20 * adv)) + 40 * sd
            else:
                # Reward being closer and getting close soon
                score += 200 * adv + 1200 // (1 + sd)
        # Small tie-break: keep moving away from being "surrounded" by opponent's proximity
        opp_dist = abs(nx - ox) + abs(ny - oy)
        score += 2 * opp_dist

        if score > best[1]:
            best = ((dx, dy), score)
        elif score == best[1]:
            # Deterministic tie-break: prefer moves that reduce distance to nearest resource
            cur_best = best[0]
            if cur_best is None:
                best = ((dx, dy), score)
            else:
                cur_dx, cur_dy = cur_best
                cur_nx, cur_ny = sx + cur_dx, sy + cur_dy
                cur_d = min(abs(cur_nx - rx) + abs(cur_ny - ry) for rx, ry in top)
                new_d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in top)
                if new_d < cur_d:
                    best = ((dx, dy), score)

    return [int(best[0][0]), int(best[0][1])]