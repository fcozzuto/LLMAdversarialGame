def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        dx = 1 if ox < sx else (-1 if ox > sx else 0)
        dy = 1 if oy < sy else (-1 if oy > sy else 0)
        return [dx, dy]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick opponent's most likely target (nearest to them); then choose moves that improve our chance at winning it or stealing another.
    opp_target = None
    best_od = None
    for x, y in resources:
        d_op = man(ox, oy, x, y)
        if best_od is None or d_op < best_od or (d_op == best_od and (x, y) < opp_target):
            best_od = d_op
            opp_target = (x, y)

    targets = resources[:]  # evaluate all, deterministic

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep in place

        # Immediate avoidance: prefer not to move closer to obstacles? (lightweight)
        min_res_dist = None
        for tx, ty in targets:
            d_me = man(nx, ny, tx, ty)
            d_op = man(ox, oy, tx, ty)
            adv = d_op - d_me  # positive means we are closer
            # Strongly prioritize resources where we can arrive before opponent.
            score = adv * 100 - d_me
            # Also bias toward opp_target to prevent them from comfortably winning their nearest.
            if opp_target == (tx, ty):
                score += 50
            if min_res_dist is None or score > min_res_dist:
                min_res_dist = score
        # If we can currently win opp_target, also encourage committing to it.
        d_me_t = man(nx, ny, opp_target[0], opp_target[1])
        d_op_t = man(ox, oy, opp_target[0], opp_target[1])
        commit = 20 if d_me_t <= d_op_t else 0

        total = min_res_dist + commit + (-(man(nx, ny, ox, oy)) * 0.01)
        if best_score is None or total > best_score or (total == best_score and (dx, dy) < best_move):
            best_score = total
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]