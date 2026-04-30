def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Select a resource where we have (or can gain) a relative distance advantage
    if resources:
        best = None
        best_key = None
        for r in resources:
            ds = dist((sx, sy), tuple(r))
            do = dist((ox, oy), tuple(r))
            key = (-(do - ds), ds, r[0], r[1])  # maximize (do-ds) => minimize negative
            if best_key is None or key < best_key:
                best_key = key
                best = tuple(r)
        target = best
    else:
        target = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)

    def choose_resource_dir(x, y, tx, ty):
        dx = 0
        if tx > x: dx = 1
        elif tx < x: dx = -1
        dy = 0
        if ty > y: dy = 1
        elif ty < y: dy = -1
        return dx, dy

    # Deterministic obstacle-aware evaluation of all local moves
    opp_dist = dist((sx, sy), (ox, oy))
    desired_dxdy = choose_resource_dir(sx, sy, target[0], target[1])
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**9
        else:
            d_to_target = dist((nx, ny), target)
            d_to_opp = dist((nx, ny), (ox, oy))
            # Main goal: reduce target distance
            score = -3 * d_to_target
            # Strategy shift: if not ahead last epoch (signal negative), be more aggressive:
            # prioritize moves that also tighten distance to opponent when we have no immediate resource
            if opp_dist > 6:
                score += 1.2 * ( -d_to_opp )
            else:
                score += 0.2 * ( -d_to_opp )
            # Mild preference to head toward direct target direction
            if (dx, dy) == desired_dxdy:
                score += 0.7
            # Encourage avoiding being stuck next to obstacles (local hazard)
            hazard = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    px, py = nx + adx, ny + ady
                    if inb(px, py) and (px, py) in obstacles:
                        hazard += 1
            score -= 0.08 * hazard

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]