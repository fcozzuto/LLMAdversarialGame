def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources:
        if p and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs:
                res.append(t)

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0); best_val = -10**18

    on_resource = set(res)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in on_resource:
            val += 1000000

        if res:
            my_best = 10**9
            opp_best = 10**9
            adv_sum = 0
            for rx, ry in res:
                dmy = cheb(nx, ny, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                if dmy < my_best: my_best = dmy
                if dop < opp_best: opp_best = dop
                if dmy < dop:
                    adv_sum += (dop - dmy)
            # Prioritize getting closer to resources, and only then beat opponent on access.
            val += -my_best * 50
            val += adv_sum * 10
            val += opp_best * 2  # slight pressure to worsen opponent's nearest resource distance
        else:
            # No resources visible: stay away from opponent while maintaining mobility
            val += cheb(nx, ny, ox, oy) * 5

        # Tie-breaker: prefer moves that don't reduce immediate freedom too much
        free = 0
        for mx, my in moves:
            tx, ty = nx + mx, ny + my
            if inb(tx, ty) and (tx, ty) not in obs:
                free += 1
        val += free * 0.1

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]