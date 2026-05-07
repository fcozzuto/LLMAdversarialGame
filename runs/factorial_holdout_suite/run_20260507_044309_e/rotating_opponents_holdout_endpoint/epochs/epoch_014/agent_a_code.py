def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target_from(x, y):
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive: we are closer in Manhattan terms
            # Prefer: (1) higher chance to beat opponent (adv), (2) shorter self distance, (3) closeness to avoid detours.
            key = (-adv, sd, abs(rx - x) + abs(ry - y), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry, sd, od, adv)
        return best

    best_dxdy = [0, 0]
    best_key = None
    cur_best = best_target_from(sx, sy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        t = best_target_from(nx, ny)
        if t is None:
            key = (0, 10**9, 10**9, 0, 0)
        else:
            rx, ry, sd, od, adv = t
            # Strongly prefer moves that keep/raise "adv" and reduce sd.
            # Slight preference for moves that also reduce opponent's nearest competition.
            key = (-adv, sd, abs(ox - rx) + abs(oy - ry), (dx, dy) == (0, 0))
        if best_key is None or key < best_key:
            best_key = key
            best_dxdy = [dx, dy]

    # If current cell is already best for us, allow staying; otherwise return computed move.
    if cur_best is not None:
        rx, ry, sd, od, adv = cur_best
        if sd == 0 and adv >= 0:
            return [0, 0]
    return best_dxdy