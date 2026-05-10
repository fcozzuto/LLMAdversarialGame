def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    # Late game: greedier pickup; early: deny opponent by contesting resources they can reach first.
    late = 1.0 if turns_remaining <= 10 else 0.0
    w_self = 1.2 + 1.0 * late
    w_race = 1.6 - 0.8 * late  # higher => prefer resources opponent can't reach first
    w_avoid_opp = 0.8 if late < 0.5 else 0.4

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp_now = cheb(nx, ny, ox, oy)
        local = -w_avoid_opp * (1 if d_opp_now <= 1 else 0)

        # Choose best target resource after this move.
        target_val = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds == 0:
                race = 0
            else:
                # Positive when we are closer; negative when opponent is closer.
                race = (do - ds)
            # Base: prefer closer. Race: contest opponent reach.
            val = -w_self * ds + w_race * race
            # Slightly prefer higher "urgency" resources when time is short.
            if turns_remaining <= 8:
                val += 0.3 * (8 - ds) - 0.2 * (8 - do)
            if val > target_val:
                target_val = val

        local += target_val
        if local > best[0]:
            best = (local, dx, dy)

    return [int(best[1]), int(best[2])]