def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    if resources:
        # Score a move by how much it improves "race" over the opponent for the best visible target
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            self_pos = (nx, ny)
            best_val = -10**18
            for r in resources:
                sr = dist(self_pos, r)
                if opp_exists:
                    orr = dist((ox, oy), r)
                    # Encourage being closer; also slightly prefer closer targets to reduce ties
                    val = (orr - sr) * 100 - sr
                else:
                    val = -sr
                if val > best_val:
                    best_val = val
            # Mild tie-break: don't step closer to opponent too much if already not winning race
            if opp_exists:
                d_to_opp = dist((nx, ny), (ox, oy))
                best_val += min(d_to_opp, 10)
            if best_val > best[0]:
                best = (best_val, dx, dy)
        return [best[1], best[2]]

    # No visible resources: move toward the center while keeping distance from opponent if possible
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = -(abs(nx - cx) + abs(ny - cy))  # center
        if opp_exists:
            sc += dist((nx, ny), (ox, oy)) * 0.3  # keep away
        if sc > best[0]:
            best = (sc, dx, dy)
    return [best[1], best[2]]