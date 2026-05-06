def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    # Pick best resource by "capture advantage" and prefer central-ish tie-break.
    best_target = resources[0]
    best_score = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        center = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        # Deterministic tuple compare
        sc = (adv, -sd, center, -rx, -ry)
        if best_score is None or sc > best_score:
            best_score = sc
            best_target = (rx, ry)

    rx, ry = best_target
    # Local evaluation for next move: minimize own distance to target while avoiding letting opponent catch up.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd1 = man(nx, ny, rx, ry)
        od1 = man(ox, oy, rx, ry)
        # If opponent is already closer, prioritize blocking by increasing their distance.
        opp_dist_now = man(ox, oy, nx, ny)
        self_to_opp = man(nx, ny, ox, oy)
        val = (
            -sd1,               # closer to target first
            (od1 - sd1),       # only good if we keep/extend advantage
            -opp_dist_now,     # stay away from opponent if possible
            -self_to_opp,      # and avoid getting too adjacent
            dx, dy              # deterministic tie-break
        )
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]