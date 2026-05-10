def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation["obstacles"]))
    resources = list(map(tuple, observation["resources"]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neigh_free(nx, ny):
        if (nx, ny) in obstacles:
            return 0
        cnt = 0
        for dx, dy in moves:
            x2, y2 = nx + dx, ny + dy
            if inb(x2, y2) and (x2, y2) not in obstacles:
                cnt += 1
        return cnt

    def best_resource():
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man((sx, sy), (rx, ry))
            opd = man((ox, oy), (rx, ry))
            lead = opd - myd
            # Prefer: we arrive earlier (lead), then closer; also prefer higher "escape room" near resource.
            room = neigh_free(rx, ry)
            cand = (-(lead), myd, -room, rx, ry)
            if best is None or cand < best:
                best = cand
        if best is None:
            return None
        return (best[3], best[4])

    target = best_resource()

    # If no viable resource, contest by moving toward opponent.
    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    best = (0, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Greedy score: distance-to-target minus advantage pressure; avoid dead-ends.
        d_my = man((nx, ny), (tx, ty))
        d_opp = man((nx, ny), (ox, oy))
        opp_d_res = man((ox, oy), (tx, ty))
        # If we are closer than opponent, prioritize getting there quickly; otherwise reduce our disadvantage.
        adv = opp_d_res - (man((nx, ny), (tx, ty)))
        dead_pen = -neigh_free(nx, ny)
        score = d_my * 2 - adv * 5 + dead_pen * 3 + d_opp * 0
        if score < best[1]:
            best = ((dx, dy), score)

    dx, dy = best[0]
    return [int(dx), int(dy)]