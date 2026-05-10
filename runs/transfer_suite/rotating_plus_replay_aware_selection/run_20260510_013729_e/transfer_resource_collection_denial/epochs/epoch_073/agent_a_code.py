def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    def best_target(px, py):
        best_adv = -10**18
        best_sd = 10**18
        best_od = 10**18
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive: we are closer (faster)
            if adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and od < best_od))):
                best_adv, best_sd, best_od = adv, sd, od
        return best_adv, best_sd, best_od

    cur_adv, cur_sd, cur_od = best_target(sx, sy)

    best_move = (0, 0)
    best_score = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        adv, sd, od = best_target(nx, ny)
        # If we can beat opponent, strongly prioritize that race; otherwise go for closest resource.
        if adv >= 0:
            score = 2.0 * adv - 0.10 * sd + 0.02 * (man(ox, oy, nx, ny))
        else:
            score = 1.0 * adv - 0.60 * sd + 0.02 * (man(ox, oy, nx, ny))
        # Small commitment to staying aligned with current advantage.
        score += 0.03 * (adv - cur_adv)
        if score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]