def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def cell_value(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        self_d = 10**9
        best_adv = -10**9
        best_res_d = 10**9
        for rx, ry in resources:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            if sd < self_d:
                self_d = sd
                best_res_d = sd
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
        # Prefer cells that:
        # 1) Make opponent farther from the best contested resource than we are.
        # 2) Reduce our own distance to resources quickly.
        # 3) Slightly prefer progress toward the nearest resource.
        return best_adv * 20 - self_d * 3 - best_res_d * 0.5

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        val = cell_value(nx, ny)
        # Deterministic tie-break: prefer staying closer to resources and then lexicographic move.
        if val > best_val:
            best_val = val
            best_move = [dx if inb(sx + dx, sy + dy) else 0, dy if inb(sx + dx, sy + dy) else 0]
        elif val == best_val:
            cand = [dx if inb(sx + dx, sy + dy) else 0, dy if inb(sx + dx, sy + dy) else 0]
            if cand[0] < best_move[0] or (cand[0] == best_move[0] and cand[1] < best_move[1]):
                best_move = cand

    return [int(best_move[0]), int(best_move[1])]