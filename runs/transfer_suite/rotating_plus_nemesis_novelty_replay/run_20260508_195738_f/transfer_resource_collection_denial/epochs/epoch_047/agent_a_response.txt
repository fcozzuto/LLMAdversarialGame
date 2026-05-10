def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            v = (manh(ox, oy, cx, cy), -manh(sx, sy, cx, cy))
            if best is None or v > best[0]:
                best = (v, (cx, cy))
        tx, ty = best[1]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for ndx, ndy in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + ndx, sy + ndy
            if inb(nx, ny):
                return [ndx, ndy]
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # tie-break: deterministic preference order after scoring (resource adjacency, then toward best delta)
    res_set = set(resources)
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d_min = 10**9
        opp_d_min = 10**9
        gain = 0
        if (nx, ny) in res_set:
            gain += 1000  # immediate pickup
        # choose best target for this move (local greedy over all remaining resources)
        for rx, ry in resources:
            my_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            if my_d < my_d_min:
                my_d_min = my_d
            if opp_d < opp_d_min:
                opp_d_min = opp_d
            # advantage on who can reach first
            g = (opp_d - my_d)
            if (rx, ry) == (nx, ny):
                g += 200
            if g > gain:
                gain = g
        # prioritize: winning race, then closer to resources, then safer from opponent (more remaining distance)
        score = (gain, -my_d_min, -(opp_d_min - my_d_min), -manh(ox, oy, nx, ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if inb(sx + best_move[0], sy + best_move[1]):
        return best_move
    return [0, 0]