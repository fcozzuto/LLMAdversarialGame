def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def bfs_dist(start, goals_set):
        if start in goals_set:
            return 0
        qx, qy, qi = [start[0]], [start[1]], 0
        dist = {(start[0], start[1]): 0}
        best = None
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            d = dist[(x, y)]
            qi += 1
            if best is not None and d >= best:
                continue
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not valid(nx, ny) or (nx, ny) in dist:
                    continue
                nd = d + 1
                if (nx, ny) in goals_set:
                    if best is None or nd < best:
                        best = nd
                dist[(nx, ny)] = nd
                qx.append(nx)
                qy.append(ny)
        return best if best is not None else 10**9
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    goals_opp_farthest = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    opp_far_set = {goals_opp_farthest}
    my_goal_set = {(ox, oy)}
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0
        my_to_opp = bfs_dist((nx, ny), my_goal_set)
        opp_to_far = bfs_dist((ox, oy), opp_far_set)
        # Prefer moves that reduce our path to opponent while shrinking opponent's progress to far corner.
        # Also add slight penalty for moving away in Manhattan terms.
        man_away = abs(ox - nx) + abs(oy - ny)
        val = -my_to_opp * 5 - (opp_to_far - my_to_opp) * 2 - man_away * 0.1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]