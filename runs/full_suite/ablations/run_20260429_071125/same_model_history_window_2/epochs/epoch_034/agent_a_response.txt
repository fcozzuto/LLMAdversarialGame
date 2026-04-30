def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    scores = observation.get("scores") or {}
    self_name = observation.get("self_name", "agent_a")
    opp_name = observation.get("opponent_name", "agent_b")
    my_score = float(scores.get(self_name, 0.0) or 0.0)
    opp_score = float(scores.get(opp_name, 0.0) or 0.0)
    behind = my_score < opp_score

    opp_d_cache = []
    for rx, ry in resources:
        opp_d_cache.append(cheb(ox, oy, rx, ry))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        val = -10**18
        for i, (rx, ry) in enumerate(resources):
            sd = cheb(nx, ny, rx, ry)
            od = opp_d_cache[i]
            gap = od - sd  # positive means we are closer than opponent
            if behind and gap < 0:
                continue
            # Prefer (1) being closer than opponent, (2) closer to resource, (3) slightly prefer larger gap
            cand = 6 * gap - sd
            if cand > val:
                val = cand

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]