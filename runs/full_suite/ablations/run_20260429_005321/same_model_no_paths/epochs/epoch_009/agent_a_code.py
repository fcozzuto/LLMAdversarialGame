def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_pen(x, y):
        pen = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in moves:
        moves.append((0, 0))

    if not resources:
        tx, ty = w - 1, h - 1
        # Head to corner opposite opponent but still avoid obstacles.
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (man(nx, ny, tx, ty), obs_pen(nx, ny), abs(dx) + abs(dy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_move = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # For this next position, choose the resource where we gain the most relative proximity.
        # Score = advantage (opp_dist - self_dist) with progress bias and obstacle avoidance.
        local_best = -10**9
        local_progress = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds
            if adv > local_best:
                local_best = adv
                local_progress = ds
            elif adv == local_best and ds < local_progress:
                local_progress = ds

        score = (local_best * 1000) - local_progress - obs_pen(nx, ny) * 2 - (dx == 0 and dy == 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score and best_move is not None:
            # Deterministic tie-break: smaller move magnitude, then towards resources.
            cur_mag = abs(dx) + abs(dy)
            best_mag = abs(best_move[0]) + abs(best_move[1])
            if cur_mag < best_mag:
                best_move = (dx, dy)
            elif cur_mag == best_mag:
                # further deterministic: prefer dx smaller then dy smaller
                if dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]):
                    best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]