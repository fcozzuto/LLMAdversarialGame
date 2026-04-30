def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obstacle_adj_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2
        return pen

    # Target heuristic switches to a more aggressive "beat opponent to nearest viable resource"
    def best_adv_from(x, y):
        if not resources:
            return -md((x, y), ((w - 1) // 2, (h - 1) // 2))
        best = None
        # maximize: (opponent_dist - my_dist) first; then my_dist smaller; then deterministic resource tie-break
        for r in resources:
            myd = md((x, y), r)
            opd = md((ox, oy), r)
            # smaller myd can still be worse if opponent is closer; we want to be earlier
            adv = opd - myd
            key = (-adv, myd, -r[0], -r[1])
            if best is None or key < best[0]:
                best = (key, adv)
        return best[1]

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # immediate goals:
        # 1) beat opponent to some resource from here
        # 2) keep distance from opponent to avoid contested captures
        # 3) avoid obstacle-adjacent tiles more strongly than before
        adv = best_adv_from(nx, ny)
        dist_to_opp = md((nx, ny), (ox, oy))
        # small preference for staying close to resources overall even when not winning
        if resources:
            nearest_my = min(md((nx, ny), r) for r in resources)
        else:
            nearest_my = md((nx, ny), ((w - 1) // 2, (h - 1) // 2))

        val = (adv, dist_to_opp, -nearest_my, -(obstacle_adj_pen(nx, ny)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]