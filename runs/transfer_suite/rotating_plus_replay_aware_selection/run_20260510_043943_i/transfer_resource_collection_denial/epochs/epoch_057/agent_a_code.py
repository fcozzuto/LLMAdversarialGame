def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        ax -= bx
        if ax < 0:
            ax = -ax
        ay -= by
        if ay < 0:
            ay = -ay
        return ax + ay

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0)

    opp_dist_now = man(sx, sy, ox, oy)
    turn = observation.get("turn_index", 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        # Deny/pressure term: avoid moving too close to opponent unless it also helps you secure a resource
        deny = -man(nx, ny, ox, oy) * 3

        best_r = -(10**18)
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Capture race: strongly prefer resources where opponent is not ahead
            val = (od - sd) * 120 - sd * 5
            # Deterministic tie-break: prefer certain geometries to reduce dithering
            val += ((rx + ry + sd + od + turn) & 1) * 2
            if sd == 0:
                val += 10000
            if val > best_r:
                best_r = val

        score = best_r + deny

        # Small preference for moves that keep relative distance trend (helps avoid back-and-forth)
        nd = man(nx, ny, ox, oy)
        if nd <= opp_dist_now:
            score += 1

        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]