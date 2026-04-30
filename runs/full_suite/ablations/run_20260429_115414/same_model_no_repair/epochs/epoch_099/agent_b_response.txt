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

    def obstacle_detour_penalty(x0, y0, xt, yt):
        # Follow greedy king steps toward target; penalize if we would step onto obstacles.
        if not obstacles:
            return 0
        x, y = x0, y0
        pen = 0
        steps = cheb(x0, y0, xt, yt)
        for _ in range(steps):
            dx = 0 if xt == x else (1 if xt > x else -1)
            dy = 0 if yt == y else (1 if yt > y else -1)
            nx, ny = x + dx, y + dy
            if (nx, ny) in blocked:
                pen += 80
            x, y = nx, ny
            if x == xt and y == yt:
                break
        return pen

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Select a target deterministically each turn: maximize opponent advantage corrected by obstacle detours.
    target = resources[0]
    best_target_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        sd = cheb(sx, sy, rx, ry) + obstacle_detour_penalty(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry) + obstacle_detour_penalty(ox, oy, rx, ry)
        adv = od - sd
        # Prefer targets we can plausibly reach (small-ish self distance) if equal.
        val = adv * 1000 - sd
        if val > best_target_val:
            best_target_val = val
            target = (rx, ry)

    tx, ty = target
    # Evaluate one-step moves: improve (opp_dist - self_dist) to target, avoid obstacles, and subtly pull away from opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nsd = cheb(nx, ny, tx, ty) + obstacle_detour_penalty(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty) + obstacle_detour_penalty(ox, oy, tx, ty)
        dist_opp_self = cheb(nx, ny, ox, oy)
        move_adv = nod - nsd
        # If we can immediately reduce competition, do it; otherwise keep distance from opponent to deny them.
        score = move_adv * 1000 + dist_opp_self * 5 - nsd
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]