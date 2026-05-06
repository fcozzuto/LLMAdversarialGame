def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # Pick a contested target: where opponent is closer (or equally close) by the most.
    best_r = None
    best_gap = -10**9
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        gap = od - sd  # positive => we are closer
        # We want opponent-closer resources, so target large (sd-od)
        opp_lead = sd - od
        if opp_lead > best_gap:
            best_gap = opp_lead
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        sd = manh(nx, ny, rx, ry)
        od = manh(ox, oy, rx, ry)

        # Estimate how much this move improves our ability to beat opponent at this target
        # (smaller is better for our distance; larger is better for opponent-relative delay).
        val = (od - sd) * 200 - sd

        # If we are already closer, defend by not letting opponent close too quickly:
        # penalize moves that move us far from the target while also drawing toward opponent.
        if manh(sx, sy, rx, ry) <= manh(ox, oy, rx, ry):
            val -= sd * 2
            val -= (manh(nx, ny, ox, oy) - manh(sx, sy, ox, oy)) * 5

        # Obstacle-aware "escape" to avoid stepping into immediate traps:
        # count available neighbor cells; fewer options => lower value.
        opts = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay):
                opts += 1
        val -= max(0, 6 - opts) * 3

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]