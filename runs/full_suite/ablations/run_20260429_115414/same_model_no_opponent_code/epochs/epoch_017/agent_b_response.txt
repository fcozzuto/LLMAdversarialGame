def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    resources = observation.get("resources") or []
    res = [(int(p[0]), int(p[1])) for p in resources]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def best_target_dist(x, y):
        if not res:
            return 10**9
        md = 10**9
        for rx, ry in res:
            d = cheb(x, y, rx, ry)
            if d < md:
                md = d
        return md

    best = (0, 0)
    best_val = -10**18
    on_res = {(rx, ry) for rx, ry in res}

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in on_res:
            self_dist = 0
        else:
            self_dist = best_target_dist(nx, ny)

        opp_dist = best_target_dist(ox, oy)

        # Prefer getting/approaching resources where we are currently closer than opponent.
        # Also avoid getting closer to opponent without improving resource contest.
        contest = (opp_dist - self_dist)
        val = 0
        if self_dist == 0:
            val += 10**6
        val += 2000 * contest

        # Mild shaping to move toward our nearer resource and away from opponent.
        val += 20 * (cheb(sx, sy, ox, oy) - cheb(nx, ny, ox, oy))
        val += 5 * (cheb(nx, ny, w // 2, h // 2) - cheb(sx, sy, w // 2, h // 2))

        # If no resources, drift toward blocking by approaching opponent.
        if not res:
            val = 1000 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))  # smaller distance is better
            val = -val

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]