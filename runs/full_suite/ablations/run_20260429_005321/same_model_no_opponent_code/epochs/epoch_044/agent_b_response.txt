def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h and (a, b) not in obstacles

    def d2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose move maximizing: we get closer to a resource while reducing opponent's advantage,
    # and we discourage moving into opponent "capture" vicinity.
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        # No visible resources: drift toward opponent-opposite corner (deterministic)
        tx, ty = 0 if (x + y) % 2 == 0 else w - 1, 0 if (x - y) % 2 == 0 else h - 1
        # fallthrough to heuristic below with synthetic target
        resources = [(tx, ty)]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        # Opponent proximity penalty
        opp_d = d2(nx, ny, ox, oy)
        prox_pen = 20 if opp_d <= 2 else (8 if opp_d <= 4 else 0)

        # Best resource to aim for (deterministic: min over resources)
        # value: we minimize our distance while maximizing opponent distance advantage
        best_for_move = 10**18
        for rx, ry in resources:
            ds = d2(nx, ny, rx, ry)
            do = d2(ox, oy, rx, ry)
            # smaller is better: we want ds-do to be smaller (ahead) and ds small
            cand = (ds - do) * 10 + ds
            if cand < best_for_move:
                best_for_move = cand

        # tie-break deterministic by preferring moves that keep closer to the "most likely" target corner
        corner_bias = (nX := nx) * 0 + (nY := ny) * 0  # no-op but deterministic placeholder removed by being 0
        val = -best_for_move - prox_pen - corner_bias

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]