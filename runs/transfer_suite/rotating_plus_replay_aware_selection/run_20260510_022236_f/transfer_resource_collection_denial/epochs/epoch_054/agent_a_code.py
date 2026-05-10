def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for ax, ay in obstacles:
        x, y = int(ax), int(ay)
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_penalty(x, y):
        if (x, y) in obs:
            return 50
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in obs:
                    pen += 2
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = []
    for rx, ry in resources:
        x, y = int(rx), int(ry)
        if inb(x, y) and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    # Pick best resource to contest: maximize (opp_dist - self_dist), then prefer closer to us, and safer near obstacles.
    best_res = None
    best_r = (-10**9, -10**9, -10**9)
    for rx, ry in res:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd
        safety = -obstacle_penalty(rx, ry)  # higher is better
        key = (advantage, -sd, safety)
        if key > best_r:
            best_r = key
            best_res = (rx, ry)

    rx, ry = best_res

    # Move one step to increase our progress toward the target while avoiding obstacles and reducing opponent chances.
    best_move = (0, 0)
    best_m = (-10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sp = obstacle_penalty(nx, ny)
        if sp >= 50:
            continue
        # Prefer reduced distance to target; also consider not letting opponent gain too much relative to us.
        nd_self = cheb(nx, ny, rx, ry)
        nd_opp = cheb(ox, oy, rx, ry)
        # If already on target, just grab: strongly prefer.
        on_target = 40 if (nx, ny) == (rx, ry) else 0
        # Tie-break deterministically by a tiny preference for not moving if equally good.
        move_cost = 0 if (dx == 0 and dy == 0) else 0.01
        score = (nd_opp - nd_self) * 10 + on_target - nd_self - sp - move_cost
        if score > best_m:
            best_m = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]