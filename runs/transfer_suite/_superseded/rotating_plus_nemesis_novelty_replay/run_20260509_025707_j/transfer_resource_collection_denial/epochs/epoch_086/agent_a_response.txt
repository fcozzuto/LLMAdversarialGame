def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Tie-break: prefer moves that avoid being closer to opponent after collection races.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Small safety penalty if we move adjacent to an obstacle (helps navigate sparse blocks).
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_pen -= 1

        # Evaluate the best race target from the next position.
        local_best_adv = -10**18
        local_best_time = 10**9
        local_best_dist = 10**9
        for r in resources:
            rx, ry = r[0], r[1]
            my_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            adv = opp_t - my_t  # positive means we are faster
            # Encourage collecting while also reducing how much we trail.
            if adv > local_best_adv:
                local_best_adv = adv
                local_best_time = my_t
                local_best_dist = my_t
            elif adv == local_best_adv:
                if my_t < local_best_time:
                    local_best_time = my_t
                    local_best_dist = my_t
                elif my_t == local_best_time and my_t < local_best_dist:
                    local_best_dist = my_t

        # Global value: maximize winning margin; if tied, choose faster collection;
        # if still tied, slightly prefer moving toward opponent's side to disrupt.
        # Use Chebyshev distance to opponent for final minor tie-break.
        opp_side_dist = cheb(nx, ny, ox, oy)
        val = (local_best_adv * 1000) - (local_best_time * 10) - opp_side_dist + adj_pen
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move