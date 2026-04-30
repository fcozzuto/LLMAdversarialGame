def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def obstacle_prox(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    best = (0, 0); best_v = -10**18
    res_set = set((r[0], r[1]) for r in resources)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue

        v = 0
        v -= 1.25 * obstacle_prox(nx, ny)
        if (nx, ny) in res_set:
            v += 120.0

        if resources:
            # Pick the resource we can "claim" most sooner than opponent
            my_best = 10**9
            opp_best = -10**9
            for rx, ry in resources:
                d_my = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                my_best = d_my if d_my < my_best else my_best
                opp_best = d_opp if d_opp > opp_best else opp_best
                # Advantage: larger means opponent farther from that resource
                adv = d_opp - d_my
                # Blend advantage with closeness
                cand = adv * 3.0 - d_my * 0.9
                if cand > v:
                    v = cand
            # Encourage moving toward some resource and away from letting opponent get closer
            v += -my_best * 0.25 + (opp_best - my_best) * 0.05

        # Mild tie-break: move generally toward board center to avoid corner traps
        cx, cy = w // 2, h // 2
        v += -0.01 * cheb(nx, ny, cx, cy)

        if v > best_v:
            best_v = v; best = (dx, dy)

    return [best[0], best[1]]