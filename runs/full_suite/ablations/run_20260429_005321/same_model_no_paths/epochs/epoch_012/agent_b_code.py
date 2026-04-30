def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    adj8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_pen(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # If resources exist, prefer moves that increase our distance advantage vs opponent
    # on high-value targets, while avoiding obstacle pressure.
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if (nx, ny) in resources:
                return [dx, dy]  # deterministically take
            self_pos_bonus = -0.35 * (man(nx, ny, 0, 0) + man(nx, ny, w - 1, h - 1)) * 0.01
            cur_val = -0.55 * obs_pen(nx, ny) + self_pos_bonus
            # Evaluate best target after moving
            local_best = -10**18
            for rx, ry in resources:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # Prefer targets where we are closer; also slightly punish being far overall.
                adv = do - ds
                # If opponent is already very close, intercept becomes more important.
                intercept_need = 1.5 if do <= 2 else 0.0
                # Mild preference to reduce both distances (faster convergence).
                conv = -(ds + do) * 0.02
                # Small tie-break to not stall: prefer targets with smaller ds primarily.
                score = adv * 2.0 + intercept_need * adv + conv - ds * 0.01
                if score > local_best:
                    local_best = score
            # Additional pressure: don't move toward squares that increase our chance of being trapped
            # relative to staying put; compare only with current penalties.
            cur_val += local_best
            # Micro-avoid cycles: prefer not to increase distance to the best resource's estimated ds.
            # (Using current best target heuristic)
            best_val_candidate = cur_val
            if best_val_candidate > best_val or (best_val_candidate == best_val and (dx, dy) < best_move):
                best_val = best_val_candidate
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: deterministically move toward the farthest corner (opponent's side),
    # while keeping distance from obstacles.
    tx, ty = w - 1, h - 1
    target = (tx, ty)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = man(nx, ny, target[0], target[1]) + 0.9 * obs_pen(nx, ny) - 0.03 * man(nx, ny, ox, oy)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]