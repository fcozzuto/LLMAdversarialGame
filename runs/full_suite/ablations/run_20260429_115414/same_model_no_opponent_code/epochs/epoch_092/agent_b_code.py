def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        # Fallback: move toward opponent line to contest.
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Estimate opponent priority: resources with highest (self_dist - opp_dist) from opponent view.
    best_my = None
    best_score = -10**18
    best_op = None
    best_op_score = -10**18

    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier and "steal" those opponent would like.
        my_score = (od - sd) * 1000 - sd
        if my_score > best_score:
            best_score = my_score
            best_my = (rx, ry)
        # Opponent would prefer reaching earlier from their standpoint.
        op_score = (sd - od) * 1000 - od
        if op_score > best_op_score:
            best_op_score = op_score
            best_op = (rx, ry)

    tx, ty = best_my
    ox2, oy2 = best_op
    # If opponent seems much closer to their top target, switch to denying: move toward that target.
    if best_op is not None:
        my_to_op = cheb(sx, sy, ox2, oy2)
        op_to_op = cheb(ox, oy, ox2, oy2)
        if my_to_op - op_to_op >= 2:
            tx, ty = ox2, oy2

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target; secondary: increase opponent distance to same target.
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(ox, oy, tx, ty)
        # Also consider slightly moving away from obstacles' immediate area to avoid traps.
        trap = 0
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) == 1:
                trap += 1
        val = (d2 - d1) * 200 - d1 - trap * 50
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]