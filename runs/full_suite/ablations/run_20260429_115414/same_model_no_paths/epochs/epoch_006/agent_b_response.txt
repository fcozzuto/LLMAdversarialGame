def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    me = tuple(observation.get("self_position", (0, 0)))
    opp = tuple(observation.get("opponent_position", (0, 0)))
    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = me[0] + dx, me[1] + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    cx, cy = w // 2, h // 2

    def obstacle_threat_score(x, y):
        # Penalize adjacency to obstacles to avoid trapping.
        if not obstacles:
            return 0
        best = 999
        for ox, oy in obstacles:
            d = cheb((x, y), (ox, oy))
            if d < best:
                best = d
        return 4 if best >= 3 else (5 - best)  # higher is worse

    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = me[0] + dx, me[1] + dy
        my_to_center = cheb((nx, ny), (cx, cy))
        opp_to_center = cheb(opp, (cx, cy))
        center_adv = opp_to_center - my_to_center

        # Resource competition: favor moves where I can reach some resource earlier than opponent,
        # and where my "best reachable" distance improves most.
        if resources:
            my_best = 999
            opp_best = 999
            win_margin = -999
            for r in resources:
                if r in obstacles:
                    continue
                dm = cheb((nx, ny), r)
                do = cheb(opp, r)
                if dm < my_best: my_best = dm
                if do < opp_best: opp_best = do
                m = do - dm  # positive means I get it earlier
                if m > win_margin: win_margin = m
            # Also include second objective: reduce opponent's advantage over my best target.
            key = (
                -win_margin,                 # maximize win_margin
                my_best,                      # minimize my distance to closest resource
                opp_best,                     # then minimize opponent's closest distance
                -center_adv,                  # then prefer central progress
                obstacle_threat_score(nx, ny) # then avoid traps
            )
        else:
            # No resources visible: just improve center while avoiding obstacles.
            key = (-center_adv, my_to_center, obstacle_threat_score(nx, ny))

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]