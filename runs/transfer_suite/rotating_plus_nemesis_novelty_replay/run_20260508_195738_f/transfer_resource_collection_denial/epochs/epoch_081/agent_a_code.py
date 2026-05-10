def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (0, 0) if ((ox + oy) % 2 == 0) else (w - 1, h - 1)
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = ds <= do
            # Primary: maximize slack (opponent advantage we can negate). Secondary: our speed. Tertiary: avoid tie-breaking traps near opponent.
            score = (-(ds - do),)  # smaller ds-do => better (we are closer or equal)
            # Convert to sortable scalar tuple without float:
            tup = (0 if lead else 1, -(do - ds), ds, -(abs(rx - ox) + abs(ry - oy)))
            if best is None or tup < best[0]:
                best = (tup, (rx, ry))
        tx, ty = best[1]

        # If opponent can take something next (distance 1), bias toward that same cell even if we're slightly behind.
        # This adds robustness against "shadow grab" behavior.
        risk_target = None
        for rx, ry in resources:
            if cheb(ox, oy, rx, ry) <= 1:
                if risk_target is None or cheb(sx, sy, rx, ry) < cheb(sx, sy, risk_target[0], risk_target[1]):
                    risk_target = (rx, ry)
        if risk_target is not None:
            rx, ry = risk_target
            if cheb(sx, sy, rx, ry) <= cheb(sx, sy, tx, ty):
                tx, ty = rx, ry

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal/step hits an obstacle, try axis-aligned deterministic fallback.
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for ndx, ndy in candidates:
        nx, ny = sx + ndx, sy + ndy
        if valid(nx, ny):
            return [ndx, ndy]
    return [0, 0]