def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}
    resources = observation.get("resources") or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target_for(posx, posy):
        if not resources:
            return None
        best = None
        best_score = None
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            d_self = man(posx, posy, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            adv = d_opp - d_self
            score = (adv, -d_self, -(rx + ry * 0))  # deterministic tie
            if best_score is None or score > best_score:
                best_score = score
                best = (rx, ry)
        return best

    nx_targets = best_target_for(sx, sy)
    if nx_targets is None:
        # No visible resources: move to reduce opponent distance
        best_move = [0, 0]
        best_d = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            if best_d is None or d < best_d:
                best_d = d
                best_move = [dx, dy]
        return best_move

    tx, ty = nx_targets
    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        adv = d_opp - d_self
        # Secondary: prefer moves that also improve distance to the next-best target
        sec_best = 10**9
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            ds = man(nx, ny, rx, ry)
            if (rx, ry) != (tx, ty) and ds < sec_best:
                sec_best = ds
        sec_best = 0 if sec_best == 10**9 else sec_best
        score = (adv, -d_self, -sec_best, -(nx + ny * 0))
        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return best_move