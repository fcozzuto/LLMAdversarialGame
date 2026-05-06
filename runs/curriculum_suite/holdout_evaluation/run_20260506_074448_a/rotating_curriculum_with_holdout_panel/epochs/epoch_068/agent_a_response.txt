def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    def center_bias(x, y):
        dx = x - cx0
        dy = y - cy0
        return - (dx * dx + dy * dy) * 0.001

    def opp_greedy_nextdist(tx, ty):
        best_d = 10**9
        best = (0, 0)
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            if d < best_d or (d == best_d and (dx, dy) < best):
                best_d = d
                best = (dx, dy)
        if best_d == 10**9:
            return man(ox, oy, tx, ty)
        return best_d

    if not resources:
        best = [0, 0]
        best_s = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            s = center_bias(nx, ny)
            if s > best_s:
                best_s = s
                best = [dx, dy]
        return best

    # Pick a "contested" target: maximize our advantage over opponent.
    best_res = None
    best_adv = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd0 = man(sx, sy, rx, ry)
        oppd0 = man(ox, oy, rx, ry)
        adv = oppd0 - myd0
        key = (adv, -myd0, -rx, -ry)
        if best_res is None or key > best_adv:
            best_adv = key
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opp_next_d = opp_greedy_nextdist(tx, ty)
        # Score: prefer states where we are closer than opponent next, and also reduce our distance.
        s = (opp_next_d - myd) + center_bias(nx, ny) - 0.03 * myd
        if s > best_score:
            best_score = s
            best_move = [dx, dy]
        elif s == best_score and (dx, dy) < tuple(best_move):
            best_move = [dx, dy]

    return best_move