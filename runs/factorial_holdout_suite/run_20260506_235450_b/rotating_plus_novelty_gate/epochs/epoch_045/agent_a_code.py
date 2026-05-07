def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2 and isinstance(p[0], int) and isinstance(p[1], int):
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources_sorted = sorted(resources, key=lambda r: (r[0], r[1]))

    # Choose best target by advantage: self closer than opponent; tie-break by smallest self distance, then lexicographic.
    best_target = None
    best_key = None
    for rx, ry in resources_sorted:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target

    # One-step greedy toward target, but only if it doesn't worsen immediate "capture likelihood".
    cur_sd = cheb(sx, sy, rx, ry)
    cur_od = cheb(ox, oy, rx, ry)
    cur_adv = cur_od - cur_sd  # higher is better

    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, rx, ry)
        adv = cur_od - nd
        immediate = 1 if any(nx == rxi and ny == ryi for rxi, ryi in resources) else 0
        # Prefer capturing now, then maximizing advantage, then minimizing distance, deterministic move preference.
        val = (immediate * 10**6) + (adv * 10**3) - nd
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)
        elif val == best_val:
            if (dxm, dym) < best_move:
                best_move = (dxm, dym)

    return [best_move[0], best_move[1]]