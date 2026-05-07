def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        cx, cy = w // 2, h // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            self_d = abs(nx - cx) + abs(ny - cy)
            opp_d = abs(nx - ox) + abs(ny - oy)
            v = -self_d + 0.01 * opp_d
            if (nx, ny) != (sx, sy):
                v += 0.001
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target that balances being close while not letting opponent take it easily.
    best_res = None
    best_score = None
    for rx, ry in resources:
        self_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        # Prefer resources where we are closer or where we can quickly improve relative position.
        score = (opp_d - self_d, -self_d, rx, ry)
        if best_score is None or score > best_score:
            best_score = score
            best_res = (rx, ry)

    tx, ty = best_res
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (sx, sy):
            move_bonus = -0.01
        else:
            move_bonus = 0.02

        self_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(nx - ox) + abs(ny - oy)
        # Primary: decrease distance to target. Secondary: reduce opponent advantage.
        # Also slightly prefer moving away from opponent to avoid denial battles.
        v = -self_d + 0.001 * opp_d + move_bonus
        # If target is adjacent, strongly prioritize it.
        if self_d == 0:
            v += 10**6
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]