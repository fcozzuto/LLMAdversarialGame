def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    res_set = set(resources)
    if (sx, sy) in res_set and (sx, sy) not in obstacles:
        return [0, 0]

    best = (0, 0)
    best_score = -10**18
    opp_res_d = {}
    for rx, ry in resources:
        opp_res_d[(rx, ry)] = cheb(ox, oy, rx, ry)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer moving to a resource we can beat/close in on faster than the opponent.
        cur_best = -10**18
        cur_tie = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            od = opp_res_d[(rx, ry)]
            lead = od - myd  # positive means we're closer
            if lead > cur_best or (lead == cur_best and myd < cur_tie):
                cur_best = lead
                cur_tie = myd

        # Extra incentive if we can land on a resource this turn.
        on_res = 1 if (nx, ny) in res_set else 0
        score = cur_best * 10 + on_res * 100 - cur_tie

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]