def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: pick a resource where we have a lead over opponent.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive if we are closer
        # Prefer: largest lead; then shorter our distance; then farther from opponent; then stable coords
        key = (-lead, sd, -od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od)
    if best is None:
        # No accessible resources: move away from opponent toward a safer corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: man(ox, oy, c[0], c[1]) - man(sx, sy, c[0], c[1]))
    else:
        _, (tx, ty), _, _ = best

    # Move choice: greedily reduce our distance, avoid stepping onto obstacles, and avoid getting too close.
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d_self = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            # Also discourage moves that bring us close while opponent is close to our target.
            d_opp_to_target = man(ox, oy, tx, ty)
            score = (d_self, -d_opp, d_opp_to_target, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move