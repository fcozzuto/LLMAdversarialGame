def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource: prefer where we are closer than the opponent.
    best_r = None
    best_trip = None  # (primary, self_dist, rx, ry) for deterministic tie-break
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        primary = od - sd  # higher => we are relatively closer
        trip = (primary, sd, rx, ry)
        if best_trip is None or trip > best_trip:
            best_trip = trip
            best_r = (rx, ry)

    rx, ry = best_r
    # Also consider a small "deny" objective: move to reduce distance to target; if we can't,
    # at least increase distance to opponent's path toward the same target.
    opp_dir = (1 if rx > ox else -1 if rx < ox else 0, 1 if ry > oy else -1 if ry < oy else 0)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_new = man(nx, ny, rx, ry)
        self_now = man(sx, sy, rx, ry)
        opp_new = man(nx, ny, ox + opp_dir[0], oy + opp_dir[1]) if inb(ox + opp_dir[0], oy + opp_dir[1]) else man(nx, ny, ox, oy)
        # Value: prioritize reaching the chosen target faster; then slightly prefer positions
        # that push against opponent approach.
        val = (-(self_new), (self_now - self_new), -opp_new, -man(nx, ny, rx, ry))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]