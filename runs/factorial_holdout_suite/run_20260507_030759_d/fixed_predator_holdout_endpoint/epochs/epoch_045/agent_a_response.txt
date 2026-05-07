def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        blocked = (nx, ny) in obs
        # if engine keeps you in place, treat blocked as staying with a penalty
        penalty = 500 if blocked else 0

        min_self_d = 10**9
        max_adv = -10**9

        for rx, ry in resources:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            if sd < min_self_d:
                min_self_d = sd
            adv = od - sd
            if adv > max_adv:
                max_adv = adv

        # Encourage leading the race; also prefer getting closer (collection progress)
        score = 3 * max_adv - min_self_d - penalty

        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]