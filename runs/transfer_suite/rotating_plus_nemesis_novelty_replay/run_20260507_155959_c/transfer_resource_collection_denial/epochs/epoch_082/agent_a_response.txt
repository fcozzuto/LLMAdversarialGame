def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (dx != 0 or dy != 0) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        if inb(sx, sy) and (sx, sy) not in obs:
            return [0, 0]
        return [0, 0]

    if not resources:
        # deterministic retreat/advance: head to farthest corner from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: man(ox, oy, c[0], c[1]))
        best = None
        for dx, dy in moves:
            nsx, nsy = sx + dx, sy + dy
            key = man(nsx, nsy, tx, ty)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Choose a target the opponent is less likely to beat: prioritize self_d <= opp_d
    best_r = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd, od = man(sx, sy, rx, ry), man(ox, oy, rx, ry)
        if best_r is None:
            best_r = (rx, ry, sd, od)
        else:
            crx, cry, csd, cod = best_r
            cur_ok = 1 if csd <= cod else 0
            new_ok = 1 if sd <= od else 0
            if new_ok != cur_ok:
                if new_ok > cur_ok:
                    best_r = (rx, ry, sd, od)
            else:
                # maximize lead; then shorter self distance
                if (od - sd, -sd) > (cod - csd, -csd):
                    best_r = (rx, ry, sd, od)

    tx, ty, _, _ = best_r

    # Move choice: go closer to target while keeping advantage vs opponent on that target
    best = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        sd = man(nsx, nsy, tx, ty)
        od = man(ox, oy, tx, ty)
        sep = man(nsx, nsy, ox, oy)
        # Primary: maximize (od - sd). Secondary: minimize sd. Tertiary: maximize separation.
        key = (od - sd, -sd, sep)
        if best is None or key > best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]