def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role") or ""

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def corner_targets():
        # Farthest-corner strategy for evader; nearest-corner for pursuer (deterministic).
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        scored = []
        for cx, cy in corners:
            dxo, dyo = cx - ox, cy - oy
            dist2 = dxo * dxo + dyo * dyo
            scored.append((dist2, cx, cy))
        scored.sort(reverse=(role == "evader"), key=lambda t: t[0])
        _, cx, cy = scored[0]
        return cx, cy

    tx, ty = corner_targets()

    best = None
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Primary: distance to opponent (maximize for evader, minimize for pursuer)
        # Secondary: distance to chosen corner (evader: far from opponent-corner, pursuer: toward it)
        c2 = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # Tertiary: keep moves that improve Manhattan separation if tie persists.
        m2 = abs(nx - ox) + abs(ny - oy)

        if role == "evader":
            val = (d2, -c2, m2)
        else:
            val = (-d2, c2, -m2)

        if best is None or val > best:
            best = val
            best_d = [dx, dy]

    if best_d is None:
        return [0, 0]
    return best_d