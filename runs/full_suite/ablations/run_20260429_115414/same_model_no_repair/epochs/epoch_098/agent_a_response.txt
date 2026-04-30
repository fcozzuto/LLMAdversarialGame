def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def local_obstacle_cost(x, y):
        if (x, y) in blocked:
            return 10**9
        cost = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                cost += 10**8
            elif d == 1:
                cost += 250
            elif d == 2:
                cost += 25
        return cost

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue

        obs_cost = local_obstacle_cost(nx, ny)
        # Score: advantage in reaching best resource + slight preference for closeness to any resource.
        best_adv = -10**18
        best_any = 10**18
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me  # higher means we can arrive earlier than opponent
            if adv > best_adv:
                best_adv = adv
            d = cheb(nx, ny, rx, ry)
            if d < best_any:
                best_any = d

        # Encourage capturing soon and avoid getting trapped near obstacles.
        val = best_adv * 1000 - best_any - obs_cost
        # Mild anti-stall: prefer moving if it doesn't reduce advantage.
        if dx == 0 and dy == 0:
            val -= 5
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]