def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    blocked = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_cost(x, y):
        if (x, y) in blocked:
            return 10**9
        cost = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                cost += 10**8
            elif d == 1:
                cost += 200
            elif d == 2:
                cost += 20
        return cost

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Choose a target where we have the biggest distance advantage.
    best_r = None
    best_adv = -10**18
    best_sd = 10**18
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if best_r is None or adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv = adv
            best_sd = sd
            best_r = (rx, ry)
    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    # Evaluate moves by estimated competitive advantage toward the chosen target, with obstacle avoidance.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        step = sd - cheb(sx, sy, tx, ty)
        # Prefer larger advantage improvement; discourage getting stuck/obstacles.
        score = (od - sd) * 1000 - sd * 5 - step * 2 - obst_cost(nx, ny)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move