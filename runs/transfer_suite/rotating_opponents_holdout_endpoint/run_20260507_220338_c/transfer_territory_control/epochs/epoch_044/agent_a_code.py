def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        try:
            obs_set.add((int(p[0]), int(p[1])))
        except:
            pass

    self_t = set(tuple(map(int, p)) for p in (observation.get("self_territory") or []) if len(p) == 2)
    opp_t = set(tuple(map(int, p)) for p in (observation.get("opponent_territory") or []) if len(p) == 2)
    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_list = []
    for p in unclaimed:
        try:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y) and (x, y) not in obs_set:
                unclaimed_list.append((x, y))
        except:
            pass

    if not unclaimed_list:
        return [0, 0]

    # Pick global target: unclaimed cell that is relatively safer for us (far from opponent), but reachable.
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_pos = (ox, oy)
    us_pos = (sx, sy)
    best_target = None
    best_tscore = None
    for tx, ty in unclaimed_list:
        d_us = dist(us_pos, (tx, ty))
        d_opp = dist(opp_pos, (tx, ty))
        # prioritize reducing our distance while keeping opponent farther
        tscore = (d_opp - d_us * 1.1, -d_us, tx, ty)
        if best_tscore is None or tscore > best_tscore:
            best_tscore = tscore
            best_target = (tx, ty)

    tx, ty = best_target

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue

        # Immediate territory value estimate
        cell = (nx, ny)
        gain = 0
        if cell in opp_t:
            gain += 2
        elif cell not in self_t:
            gain += 1

        # Frontier bias: prefer expanding near our territory
        frontier = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nb = (nx + ax, ny + ay)
                if nb in self_t:
                    frontier += 1

        # Target progress
        d_now = abs(sx - tx) + abs(sy - ty)
        d_next = abs(nx - tx) + abs(ny - ty)
        progress = d_now - d_next

        # Also slight penalty if moving closer to opponent target
        d_opp_now = abs(ox - tx) + abs(oy - ty)
        d_opp_next = abs(ox - nx) + abs(oy - ny)

        val = (gain * 10 + frontier * 2 + progress * 3 + (d_opp_next - d_opp_now) * 0.5, -abs(d_next), nx, ny, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]