def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    my = (sx, sy)
    opp = (ox, oy)

    best_need = -10**9
    best_target = None
    best_self = None
    for r in resources:
        if r in obstacles:
            continue
        dS = cheb(my, r)
        dO = cheb(opp, r)
        need = dO - dS
        if (need > best_need) or (need == best_need and (best_target is None or dS < cheb(my, best_target))):
            best_need, best_target = need, r
        if best_self is None or dS < cheb(my, best_self):
            best_self = r

    target = best_target if best_need > 0 else best_self

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    contest = (best_need > 0)
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        new = (nx, ny)
        dS = cheb(new, target)
        dO = cheb(opp, target)
        # Prefer collecting race-critical targets; also deny opponent progress if contesting.
        # Deterministic tie-break: smaller (dO - dS), then lexicographic move.
        val = 0
        if contest:
            val = (dS <= cheb(my, target) and 2000 or 0) - (dS * 10) + (max(0, best_need) * 3)
            val += (-dO) * 2  # small pressure: keep opponent from easy captures
        else:
            val = 3000 - (dS * 12) - (dO * 2)
        if val > best_val or (val == best_val and (dO - dS, dx, dy) < (0, best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0) and (sx, sy) in resources:
        return [0, 0]
    return [best_move[0], best_move[1]]