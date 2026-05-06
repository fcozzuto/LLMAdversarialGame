def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    resources_list = observation.get("resources") or []
    resources = [(r[0], r[1]) for r in resources_list]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = None
        best_sc = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -dist2(nx, ny, tx, ty) + 0.001 * dist2(nx, ny, ox, oy)
            if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    def min_res_d2(x, y):
        best = None
        for rx, ry in resources:
            d = dist2(x, y, rx, ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**18

    best = None
    best_sc = None
    opp_d = min_res_d2(ox, oy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = min_res_d2(nx, ny)
        lead = opp_d - my_d  # positive if we are closer to the nearest resource than opponent
        sc = 1000 * lead - my_d + 0.001 * dist2(nx, ny, ox, oy)
        if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]