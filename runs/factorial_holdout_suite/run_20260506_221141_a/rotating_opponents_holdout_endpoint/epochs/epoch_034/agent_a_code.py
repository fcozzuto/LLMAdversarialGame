def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_resource = None
    best_val = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer closer to us, and where we are significantly closer than opponent
        val = (myd + 0.15) - 0.55 * opd
        if best_val is None or val < best_val or (val == best_val and (rx, ry) < best_resource):
            best_val = val
            best_resource = (rx, ry)
    rx, ry = best_resource

    opp_dist = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, rx, ry)
        # Avoid getting too close to opponent unless it still advances us
        nd_op = cheb(nx, ny, ox, oy)
        opp_pen = 0.0
        if nd_op <= 1:
            opp_pen = 0.7
        # Prefer reducing distance; break ties toward positions that maintain lead and are lexicographically consistent
        lead = cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)
        score = nd + opp_pen + 0.12 * lead
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]