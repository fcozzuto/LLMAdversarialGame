def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    # Pick move maximizing guaranteed capture advantage:
    # prioritize resources where we are closer than opponent; then minimize our distance.
    # If none, still minimize (our_dist - opp_dist) and avoid stepping into opponent-advantaged immediate captures.
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if (dx != 0 or dy != 0) and not valid(nx, ny):
            continue

        local_best = 10**18
        local_beat = -10**18
        local_self = 10**18
        local_opp = 10**18

        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            diff = od - sd  # positive means we are closer
            # Prefer beating opponent, then smaller self distance, then breaking ties by farther opponent
            if diff > local_beat or (diff == local_beat and (sd < local_self or (sd == local_self and od > local_opp))):
                local_beat = diff
                local_self = sd
                local_opp = od

        # Secondary shaping: avoid moves that give opponent an immediate best advantage.
        opp_best_diff = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            od2 = man(ox, oy, rx, ry)
            sd2 = man(nx, ny, rx, ry)
            d2 = od2 - sd2
            if d2 > opp_best_diff:
                opp_best_diff = d2

        # Objective: maximize beat margin; if tie, minimize our distance; penalize if we lose badly.
        val = local_beat * 1000 - local_self
        if local_beat < 0:
            val -= (-local_beat) * 50
        # Mild penalty for entering region where opponent is much closer to any resource
        val -= max(0, (-opp_best_diff)) * 5

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]