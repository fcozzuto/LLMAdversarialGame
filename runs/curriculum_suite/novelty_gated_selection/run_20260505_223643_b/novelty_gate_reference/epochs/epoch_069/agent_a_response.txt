def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Choose move that maximizes best achievable advantage from the resulting position.
    # Also penalize being closer to opponent than ourselves (prevents "helping" them).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        cur_best = None
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Advantage: we prefer resources opponent can't reach quickly.
            adv = od - sd
            # Tie-breakers: reduce self distance, prefer diagonal progress, favor smaller coords.
            diag = -abs((tx - nx) - (ty - ny))
            tie = -(sd) + diag * 0.01 - (tx * 1e-4 + ty * 1e-6)

            # Penalize targets where opponent would already be strictly closer than us by a lot.
            pressure = -(sd - od) if od - sd > 3 else 0.0
            val = adv + tie + pressure

            if cur_best is None or val > cur_best:
                cur_best = val

        if cur_best is None:
            continue

        # Additional discouragement: don't move into squares that make us much closer to opponent.
        opp_closer_penalty = -man(nx, ny, ox, oy) * 0.001
        final_val = cur_best + opp_closer_penalty

        if best_val is None or final_val > best_val:
            best_val = final_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]