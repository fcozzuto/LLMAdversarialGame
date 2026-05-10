def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1, h - 1)
        if sx < w // 2:
            tx = w // 2
        else:
            tx = 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    opp_d = []
    for rx, ry in resources:
        opp_d.append((rx, ry, dist8(ox, oy, rx, ry)))
    opp_d.sort(key=lambda t: t[2])

    # Consider only closest few resources for stability
    k = 6 if len(opp_d) > 6 else len(opp_d)
    cand = opp_d[:k]

    best_val = -10**18
    best_move = [0, 0]

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        # Greedy score: we want to be earlier than opponent on high-priority resources
        for rx, ry, od in cand:
            nd = dist8(nx, ny, rx, ry)
            # Strongly prefer grabbing a resource this turn
            if nd == 0:
                val += 10000
            # Prefer smaller advantage (opponent later)
            adv = od - nd
            val += adv * (1 + (10 - od) * 0.05)
            # If opponent is very close, deny it by reducing their advantage
            if od <= 2:
                val -= nd * 2
        # Slight preference for closer overall to reduce dithering
        if resources:
            val -= 0.1 * min(dist8(nx, ny, rx, ry) for rx, ry in resources)

        if val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]