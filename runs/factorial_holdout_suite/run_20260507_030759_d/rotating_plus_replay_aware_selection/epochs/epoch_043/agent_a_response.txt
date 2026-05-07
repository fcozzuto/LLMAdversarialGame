def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def obstacle_proximity(x, y):
        # higher is better (far from obstacles); use nearest obstacle manhattan
        if not obstacles_list:
            return 5
        best = 10**9
        for ox2, oy2 in obstacles_list:
            d = man(x, y, ox2, oy2)
            if d < best:
                best = d
                if best == 0:
                    return -1
        return best

    best_total = -10**18
    best_sd = 10**18
    best_od = 10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        base = obstacle_proximity(nx, ny)
        move_best = -10**18
        move_best_sd = 10**18
        move_best_od = 10**18

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            # prefer contested wins (high adv), then shorter self distance, then further from opponent
            total = adv * 1000 - sd * 3 - od + base
            if total > move_best or (total == move_best and (sd < move_best_sd or (sd == move_best_sd and od < move_best_od))):
                move_best = total
                move_best_sd = sd
                move_best_od = od

        if move_best > best_total or (move_best == best_total and (move_best_sd < best_sd or (move_best_sd == best_sd and move_best_od < best_od))):
            best_total = move_best
            best_sd = move_best_sd
            best_od = move_best_od
            best_move = [dx, dy]

    return best_move