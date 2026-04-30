def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def block_penalty(x, y):
        # count obstacles in 8-neighborhood
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    target_center = (w // 2, h // 2)
    valid_resources = [r for r in resources if (r[0], r[1]) not in obstacles]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if valid_resources:
            move_score = -block_penalty(nx, ny) * 0.6
            # Evaluate immediate advantage at next positions across all resources
            for rx, ry in valid_resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer resources opponent cannot reach as fast (or at all)
                advantage = opd - myd
                # Encourage going to closer resources; discourage giving opponent a stronger race
                race_penalty = 0
                if opd <= myd:
                    race_penalty = (myd - opd) * 2.5 + 1.5
                # Add a slight pull toward the resource to break ties deterministically
                closeness_bonus = (8 - myd) * 0.35
                move_score += advantage * 3.2 - race_penalty + closeness_bonus
            # Normalize by number of resources to reduce epoch-dependent scaling
            move_score /= (len(valid_resources) if len(valid_resources) else 1)
        else:
            # No resources visible: drift toward center while avoiding obstacle pressure
            cx, cy = target_center
            v = -cheb(nx, ny, cx, cy)
            move_score = v * 1.2 - block_penalty(nx, ny) * 0.6

        # Deterministic tie-break: prefer smaller dx, then smaller dy
        if move_score > best_score or (move_score == best_score and (dx, dy) < best_move):
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]