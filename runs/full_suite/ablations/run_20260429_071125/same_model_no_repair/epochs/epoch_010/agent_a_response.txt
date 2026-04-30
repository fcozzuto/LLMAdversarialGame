def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    adj = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def hazard(x, y):
        c = 0
        for dx, dy in adj:
            nx, ny = x + dx, y + dy
            if (nx, ny) in occ: c += 1
        return c

    # Pick a target resource with a distance advantage; if none, pick best for us.
    target = None
    best_adv = None
    best_key = None
    for rx, ry in resources:
        da = d(sx, sy, rx, ry)
        db = d(ox, oy, rx, ry)
        adv = da - db
        # prefer self-closer (adv smaller/negative); then closer to us; then deterministic tie.
        key = (adv, da, ry, rx)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    # Determine our move: greedily reduce distance to target while penalizing hazard and stopping.
    tx, ty = target if target is not None else ((w - 1) // 2, (h - 1) // 2)
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        dist_to_target = d(nx, ny, tx, ty)
        # Encourage advancing toward target and avoid dangerous obstacle-adjacent cells.
        val = dist_to_target + 0.6 * hazard(nx, ny) + (0.25 if dx == 0 and dy == 0 else 0.0)
        # Also slightly discourage stepping into cells that reduce opponent's advantage too much.
        if resources:
            opp_best = 10**9
            for rx, ry in resources:
                opp_best = min(opp_best, d(ox, oy, rx, ry))
            # mild term: if opponent is close to some resource, don't idle near obstacles
            val += 0.05 * (opp_best / (w + h))
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]