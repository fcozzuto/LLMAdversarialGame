def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mx, my in cand:
            if valid(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def neighbors_count(x, y):
        c = 0
        for dx2, dy2 in cand:
            nx, ny = x + dx2, y + dy2
            if valid(nx, ny):
                c += 1
        return c

    best_score = None
    best_move = (0, 0)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate best resource from the candidate position
        best_res = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we are (and will be) closer to than opponent
            # score: higher is better
            advantage = (od - sd)  # positive if we're closer
            # Encourage actually collecting sooner and not being stuck in tight spots
            pick = (advantage, -sd, rx + ry, -neighbors_count(nx, ny))
            if best_res is None or pick > best_res:
                best_res = pick

        adv, neg_sd, _, neg_nbrs = best_res
        # Global tie-break: prefer reducing distance to chosen resource and increasing distance from opponent
        # via a simple secondary score component
        # Also slightly prefer moves that don't let opponent get closer to us
        opp_closeness = man(ox, oy, nx, ny)
        score = (adv, neg_sd, neg_nbrs, -opp_closeness)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]