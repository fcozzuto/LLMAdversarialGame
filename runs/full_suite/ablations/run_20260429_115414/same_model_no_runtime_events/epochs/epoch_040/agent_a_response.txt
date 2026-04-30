def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    if not resources:
        return [0, 0]

    rem = observation.get("remaining_resource_count", len(resources))
    try:
        rem = int(rem)
    except:
        rem = len(resources)
    late = rem <= 4

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        myd_to = []
        oppd_to = []
        for rx, ry in resources:
            myd_to.append(cheb(nx, ny, rx, ry))
            oppd_to.append(cheb(ox, oy, rx, ry))

        # Find the best resource to secure next, favoring states where we're not slower.
        best_r = -1
        best_gain = -10**18
        for i, (myd, oppd) in enumerate(zip(myd_to, oppd_to)):
            gain = (oppd - myd)
            # In late game, prioritize getting any resource quickly.
            if late:
                gain = 2 * gain - myd
            else:
                gain = 3 * gain - 0.3 * myd
            # Tie-break deterministically by resource coordinate.
            if gain > best_gain:
                best_gain = gain
                best_r = i
            elif gain == best_gain and resources[i] < resources[best_r]:
                best_r = i

        # Primary: secure resource we can reach earlier (or at least reduce the gap).
        myd = myd_to[best_r]
        oppd = oppd_to[best_r]
        gain = oppd - myd

        # Secondary: if not able to secure, still move closer and avoid being too close to opponent.
        my_to_best = -myd
        opp_dist_after = cheb(nx, ny, ox, oy)
        avoid = opp_dist_after if late else 0.2 * opp_dist_after

        val = 20 * gain + 5 * my_to_best + avoid

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]