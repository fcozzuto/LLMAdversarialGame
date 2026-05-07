def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    good = []
    deny = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if sd <= od:
            good.append((od - sd, -sd, rx, ry))
        else:
            # deny: opponent is closer; prefer nearer opponent targets and reachable ones
            reach = sd
            urgency = -od
            deny.append((urgency - reach, -reach, rx, ry))
    if good:
        # target set: where we can win (or at least tie)
        good.sort(reverse=True)
        primary = (good[0][2], good[0][3])
    else:
        deny.sort(reverse=True)
        primary = (deny[0][2], deny[0][3])

    px, py = primary
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        self_to_p = man(nx, ny, px, py)
        opp_to_p = man(ox, oy, px, py)
        advantage = opp_to_p - self_to_p  # positive => we are closer to primary

        # also consider best available "win" after our move
        best_win = -10**9
        best_block = -10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd <= od:
                # maximize how much closer we become
                v = od - sd
                if v > best_win:
                    best_win = v
            else:
                # if we can't win them, try to reduce opponent's lead (deny)
                v = (od - sd) * (-1) - sd  # smaller opponent lead and closer ourselves is better
                if v > best_block:
                    best_block = v

        # deterministic tie-break: prefer smaller self distance to primary, then lexicographic move
        key = (2 * advantage + best_win + 0.5 * best_block, -self_to_p, -man(ox, oy, nx, ny), dx, dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]