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
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Candidate evaluation: maximize denial potential of best reachable resource,
    # with a small push to approach that resource.
    cand_moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None

    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would reject; keep deterministic evaluation

        # If moving into a resource square, prioritize heavily (self pickup benefit + denying).
        on_resource_bonus = 0.0
        if (nx, ny) in resources:
            on_resource_bonus = 1000.0

        # Determine best denial target from this hypothetical position.
        # If multiple resources, prefer those where opponent is closer than we are; also favor closer targets.
        local_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            denial = od - sd
            # center bias to reduce oscillations; deterministic and mild
            cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
            center = -(((rx - cx0) ** 2 + (ry - cy0) ** 2) * 1e-4)
            # Prefer higher denial; tie-break with smaller sd, then smaller od
            t = (denial * 10.0 + center, -sd, -od, rx, ry)
            if local_best is None or t > local_best:
                local_best = t
        score = on_resource_bonus + local_best[0] + local_best[1] * 0.01 + local_best[2] * 0.001
        # Final deterministic tie-break: prefer moves with smaller dx, then smaller dy
        tmain = (score, -abs(dx), -abs(dy), dx, dy)
        if best is None or tmain > best:
            best = tmain
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]