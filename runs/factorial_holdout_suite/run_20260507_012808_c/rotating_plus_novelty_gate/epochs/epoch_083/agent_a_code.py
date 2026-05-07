def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    best = None  # (gain, tie, x, y)
    for (rx, ry) in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        gain = od - sd  # higher means we are closer than opponent
        tie = -min(sd, od)  # prefer closer overall
        if best is None or (gain, tie, -rx, -ry) > (best[0], best[1], -best[2], -best[3]):
            best = (gain, tie, rx, ry)

    tx, ty = best[2], best[3]

    # If opponent is also very close, prefer a slightly farther alternative that denies them (negative gain not too large).
    if best[0] < 0 and len(resources) > 1:
        second = None
        for (rx, ry) in resources:
            if (rx, ry) == (tx, ty):
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            gain = od - sd
            if gain < best[0]:
                continue
            # prefer not worse than current gain but with better self closeness
            tie = -sd
            if second is None or (gain, tie) > (second[0], second[1]):
                second = (gain, tie, rx, ry)
        if second is not None:
            tx, ty = second[2], second[3]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # prioritize reducing distance to target; secondary: avoid giving opponent an advantage nearby
        self_d = man(nx, ny, tx, ty)
        opp_to_target = man(ox, oy, tx, ty)
        # penalty if we step "away" from target compared to staying
        stay_d = man(sx, sy, tx, ty)
        away_pen = self_d - stay_d
        val = (0 - self_d, away_pen, -abs((nx - ox)) - abs((ny - oy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]