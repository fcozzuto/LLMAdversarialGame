def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            resources.append((x, y))
    if not resources:
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    remaining = int(observation.get("remaining_resource_count") or len(resources))
    # Preference to earlier collection; stronger when fewer resources remain.
    collect_weight = 1.0 + (12 - min(12, remaining)) * 0.06

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Evaluate move by the best resource you could secure next given opponent distance.
        # Score: higher is better. Positive means you are closer than opponent to that resource.
        move_best = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # If opponent is closer, strongly penalize; otherwise reward speed.
            advantage = opp_d - self_d
            speed = -self_d
            # Small deterministic bias to reduce dithering.
            bias = -0.001 * (rx + 3 * ry)
            val = (advantage * 2.2 + speed * 0.9) * collect_weight + bias
            if val > move_best:
                move_best = val

        # Secondary tie-break: prefer moves that reduce your distance to the currently most threatened resource.
        if move_best > best_val:
            best_val = move_best
            best_move = (dx, dy)
        elif move_best == best_val:
            tie = min((man(nx, ny, r[0], r[1]) for r in resources))
            curtie = min((man(sx + best_move[0], sy + best_move[1], r[0], r[1]) for r in resources))
            if tie < curtie:
                best_move = (dx, dy)

    bx, by = best_move
    if bx == 0 and by == 0:
        return [0, 0]
    return [int(bx), int(by)]