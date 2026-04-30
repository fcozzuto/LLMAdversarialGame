def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def nearest_dist(x, y, rlist):
        if not rlist:
            return 10**9
        m = 10**9
        for rx, ry in rlist:
            d = cheb(x, y, rx, ry)
            if d < m:
                m = d
        return m

    def opponent_next_pos():
        if not resources:
            return ox, oy
        # Assume opponent greedily reduces its nearest-resource Chebyshev distance.
        best_d = 10**9
        best = (ox, oy)
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = nearest_dist(nx, ny, resources)
            if d < best_d:
                best_d = d
                best = (nx, ny)
        return best

    oppx, oppy = opponent_next_pos()
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        own_hit = 1 if (nx, ny) in set(resources) else 0
        own_d = nearest_dist(nx, ny, resources)
        if own_hit:
            score = 10**7 - own_d
        else:
            # Promote taking resources sooner while pushing opponent away from their nearest.
            opp_d_before = nearest_dist(opx := oppx, opy := oppy, resources)
            # If we move closer to resources, opponent is presumed not benefitting; we approximate by penalizing
            # opponent progress potential after our step by comparing their distance to our candidate cell.
            # (Different from pure "go to nearest resource" policy.)
            opp_d_after = min(cheb(opx, opy, rx, ry) for rx, ry in resources) if resources else 10**9
            # Combine: lower our distance, higher opponent distance after their greedy step.
            score = (-own_d) + (0.7 * (opp_d_after - opp_d_before)) + (-0.05 * (cheb(ox, oy, nx, ny)))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]