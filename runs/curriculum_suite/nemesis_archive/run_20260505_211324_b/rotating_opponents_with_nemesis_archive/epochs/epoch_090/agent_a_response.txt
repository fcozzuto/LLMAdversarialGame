def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a resource we're relatively closer to than the opponent (favor taking advantage).
    # If none is favorable, pick the one with smallest self distance.
    best_r = None
    best_key = None
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (sd - od, sd)  # smaller is better
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Evaluate: move that best improves our lead to the chosen resource,
    # while reducing opponent's ability to immediately snatch it (via lead score).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # higher is better (we get closer than opponent)
        # Also discourage marching toward a cell that makes the opponent closer to the same resource.
        opp_step_options = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        min_opp_sd_next = 10**9
        for kx, ky in opp_step_options:
            mx, my = ox + kx, oy + ky
            if 0 <= mx < w and 0 <= my < h and (mx, my) not in obs:
                min_opp_sd_next = min(min_opp_sd_next, man(mx, my, rx, ry))
        opp_pressure = min_opp_sd_next  # smaller means opponent can take sooner
        # Combine: maximize lead, but also minimize opponent pressure. Slightly prefer closer self distance.
        val = (lead, -opp_pressure, -sd)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]