def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def free(x, y):
        return (x, y) not in obstacles

    # Choose move that maximizes our advantage over the best resource contest.
    best = None  # (value_tuple, dx, dy)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if not free(nx, ny):
            continue

        my_d = cheb(nx, ny, ox, oy)
        # For each resource: advantage = (opp_dist - self_dist). Higher means we're closer.
        # Prefer high advantage; if tied, prefer closer to a contested resource and moving away from opponent.
        best_adv = None
        best_self_d = None
        for rx, ry in resources:
            if not free(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_self_d):
                best_adv = adv
                best_self_d = sd

        if best_adv is None:
            best_adv = -10**9
            best_self_d = 0

        # Encourage distancing from opponent when advantages are not strong.
        value = (best_adv, -best_self_d, my_d)
        if best is None or value > best[0]:
            best = (value, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]