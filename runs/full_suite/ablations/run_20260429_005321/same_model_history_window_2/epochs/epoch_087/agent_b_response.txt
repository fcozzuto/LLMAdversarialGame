def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources = resources[:]

    if not resources:
        # Drift to center while keeping deterministic preference
        cx, cy = w // 2, h // 2
        best = None
        best_d = 10**9
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, cx, cy)
            if d < best_d:
                best_d, best_move = d, (dx, dy)
        return [best_move[0], best_move[1]]

    # Compute opponent distances once; our move decides who can get which resource first
    opp_dists = {}
    for rx, ry in resources:
        opp_dists[(rx, ry)] = cheb(ox, oy, rx, ry)

    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            # invalid move => engine keeps us in place; treat as staying
            nx, ny = sx, sy
        val = 0
        for rx, ry in resources:
            d_ours = cheb(nx, ny, rx, ry)
            d_opp = opp_dists[(rx, ry)]
            # prefer being strictly closer; encourage shorter races
            if d_ours < d_opp:
                val += 100 - d_ours * 3
            elif d_ours == d_opp:
                val += 5 - d_ours
            else:
                # being farther is bad, especially if we are likely to lose the resource race
                val -= 50 + (d_ours - d_opp) * 8
        # small preference: also reduce average distance to all resources
        avgd = 0
        for rx, ry in resources:
            avgd += cheb(nx, ny, rx, ry)
        avgd = avgd // len(resources)
        val -= avgd
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]