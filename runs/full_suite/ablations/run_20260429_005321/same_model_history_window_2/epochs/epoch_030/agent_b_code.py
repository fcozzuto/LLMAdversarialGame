def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best_target = None
    best_val = None
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # maximize how much closer we are than opponent; prefer fewer remaining "turn distance"
            advantage = do - ds
            # tie-break: prefer reducing our distance, and prefer more "central" resources deterministically
            val = (advantage, -ds, -((rx * 7 + ry) % 11), -rx, -ry)
            if best_val is None or val > best_val:
                best_val = val
                best_target = (rx, ry)

    tx, ty = (best_target if best_target is not None else (ox, oy))

    # choose one step that improves toward target while avoiding moving adjacent to opponent too often
    opp_dist_now = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        ds1 = cheb(sx, sy, tx, ty)
        step_progress = ds1 - ds2  # positive if closer
        opp_dist2 = cheb(nx, ny, ox, oy)
        # avoid giving opponent immediate advantage: don't step into positions where opponent is much closer to our target
        opp_to_target = cheb(ox, oy, tx, ty)
        opp_closeness = opp_to_target - cheb(nx, ny, tx, ty)  # lower is better
        risk = 0
        if opp_dist2 <= 1:
            risk = 3
        if opp_dist_now <= 2 and opp_dist2 < opp_dist_now:
            risk += 1
        # deterministic tie-break via move ordering and coords
        score = (step_progress, -ds2, -opp_closeness, opp_dist2, -(risk), -((nx * 13 + ny) % 17))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]