def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        x = ax - bx
        if x < 0: x = -x
        y = ay - by
        if y < 0: y = -y
        return x + y

    if not resources:
        return [0, 0]

    res_set = set((p[0], p[1]) for p in resources)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    # Prefer resources where we are (or can become) no slower than the opponent.
    opp_best = {}
    for rx, ry in resources:
        opp_best[(rx, ry)] = man(ox, oy, rx, ry)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in res_set:
            return [dx, dy]

        total = 0
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = opp_best[(rx, ry)]
            # If we can arrive first (or tie), strongly prefer.
            if d_self <= d_opp:
                total += 20 - d_self
            else:
                # If opponent is clearly closer, discourage.
                gap = d_self - d_opp
                total -= 6 + 2 * gap
            # Extra emphasis on nearer resources for general progress.
            total += -0.2 * d_self

        # Small direct pressure to approach opponent (denier-style) when hopeless.
        if total < 0:
            total += 0.4 * (man(sx, sy, ox, oy) - man(nx, ny, ox, oy))

        if total > best_score:
            best_score = total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]