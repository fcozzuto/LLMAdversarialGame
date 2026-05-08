def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = sorted(moves, key=lambda d: (d[0] == 0 and d[1] == 0, d[0], d[1]))

    def clamp(nx, ny):
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return nx, ny
        return sx, sy

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = man((sx, sy), (cx, cy))
            cand = (d, cx, cy)
            if best is None or cand < best:
                best = cand
        tx, ty = (best[1], best[2]) if best else (w - 1, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_move = (None, -10**9, None)
    for dx0, dy0 in moves:
        nx, ny = clamp(sx + dx0, sy + dy0)
        self_pos = (nx, ny)
        best_res = None
        # Prefer resources where we are closer than opponent; break ties by being closer to resource.
        for r in resources:
            self_d = man(self_pos, r)
            opp_d = man((ox, oy), r)
            adv = opp_d - self_d
            cand = (adv, -self_d, r[0], r[1])
            if best_res is None or cand > best_res:
                best_res = cand
        # Also lightly prefer moves that reduce distance to the best resource.
        score = (best_res[0], best_res[1])
        if score > (best_move[1], best_move[2] if best_move[0] is not None else -10**9):
            best_move = ((dx0, dy0), best_res[0], best_res[1])

    return [int(best_move[0][0]), int(best_move[0][1])]