def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res_set = set((p[0], p[1]) for p in resources)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_key = None

    # Deterministic tie-break: prefer lower dx,dy lexicographically after sorting.
    for dx0, dy0 in sorted(moves):
        nx, ny = sx + dx0, sy + dy0
        if not valid(nx, ny):
            continue

        # Immediate capture bonus
        capture = 1 if (nx, ny) in res_set else 0

        # For contest targets, maximize our advantage after this move.
        # If we move onto a resource, capture dominates.
        best_adv = -10**9
        # Also keep a secondary measure to move toward "high pressure" targets.
        best_self_dist = 10**9

        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive favors us
            if (adv > best_adv) or (adv == best_adv and self_d < best_self_dist):
                best_adv = adv
                best_self_dist = self_d

        # Mild preference to reduce our distance to the closest resource overall (robustness).
        closest_d = min(man(nx, ny, rx, ry) for rx, ry in resources) if resources else 0

        # Key: capture first, then maximize advantage, then minimize our distance, then stable tie-break.
        key = (0 if capture else 1, -best_adv, best_self_dist, closest_d, dx0, dy0)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx0, dy0)

    return [int(best[0]), int(best[1])]