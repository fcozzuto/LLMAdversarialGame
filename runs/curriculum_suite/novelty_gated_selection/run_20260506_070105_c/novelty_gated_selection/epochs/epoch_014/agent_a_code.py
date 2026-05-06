def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Two-layer deterministic heuristic: (1) capture pressure on resources where we can beat opponent,
    # (2) denial pressure: moves that increase opponent distance to their best resource.
    best = (None, -10**18)
    cur_my_min = min(man(sx, sy, rx, ry) for rx, ry in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_ds = [man(nx, ny, rx, ry) for rx, ry in resources]
        opp_ds = [man(ox, oy, rx, ry) for rx, ry in resources]

        my_best = min(my_ds)
        opp_best = min(opp_ds)

        # Capture/deny mix.
        # Encourage: being closer than opponent on contested resources; discourage: letting opponent get closer.
        cap = 0.0
        deny = 0.0
        for myd, oppd in zip(my_ds, opp_ds):
            # Relative advantage for this resource
            rel = oppd - myd
            weight = 1.0 / (1.0 + myd)
            if rel > 0:
                cap += rel * weight * 2.2
            else:
                deny += (-rel) * weight * 1.6

        # Direct denial: increase opponent's nearest-resource distance (resource_denier counterplay).
        denial_pressure = opp_best - min(opp_ds)  # always 0 here; keep deterministic structure
        denial_pressure = (opp_best - (min(opp_ds) if resources else opp_best))  # redundant but safe

        # Slight preference to not stall, plus gentle progress toward nearest.
        progress = cur_my_min - my_best
        score = (cap - deny) * 6.0 + (opp_best - my_best) * 1.2 + progress * 0.9 - (my_best * 0.02)

        # Deterministic tie-break: prefer smaller my_best, then prefer non-stay, then lexicographic move.
        if score > best[1] + 1e-9:
            best = ((dx, dy), score)
        elif abs(score - best[1]) <= 1e-9:
            if best[0] is None:
                best = ((dx, dy), score)
            else:
                bdx, bdy = best[0]
                bx, by = bdx, bdy
                if my_best < min(man(sx + bx, sy + by, rx, ry) for rx, ry in resources):
                    best = ((dx, dy), score)
                elif (dx, dy) != (0, 0) and (bx, by) == (0, 0):
                    best = ((dx, dy), score)
                elif (dx, dy) < (bx, by):
                    best = ((dx, dy), score)

    return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]