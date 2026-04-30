def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    grid_w, grid_h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        dx = -1 if x > 0 else 0
        dy = -1 if y > 0 else 0
        if (x + dx, y + dy) in obstacles:
            return [0, 0]
        return [dx, dy]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_r = None
    best_s = -10**18
    for rx, ry in resources:
        my_d = cheb(x, y, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Prefer resources I can reach clearly sooner; also avoid very far ones.
        s = (opp_d - my_d) * 3 - my_d
        # Small bias toward current quadrant to avoid dithering.
        if rx <= grid_w // 2:
            s += 0.5
        if ry <= grid_h // 2:
            s += 0.5
        if s > best_s:
            best_s = s
            best_r = (rx, ry)

    rx, ry = best_r
    opp_dist = cheb(x, y, ox, oy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_v = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= grid_w or ny < 0 or ny >= grid_h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, rx, ry)
        od = cheb(nx, ny, ox, oy)
        # Strongly avoid moving into tight proximity with opponent.
        v = -nd * 6
        if (nx, ny) == (rx, ry):
            v += 50
        v -= (2 - od) * 10 if od < 2 else 0
        # Slightly reduce chances opponent captures by not lingering when they are near target.
        if opp_dist <= 2:
            v += (od - opp_dist) * 1.5
        # If stuck, deterministic tie-breaker: prefer staying still less? choose lexicographically smallest.
        if v > best_v or (v == best_v and (dx, dy) < best_m):
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]