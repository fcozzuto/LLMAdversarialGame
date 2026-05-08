def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_c = abs(nx - cx) + abs(ny - cy)
        d_o = abs(nx - ox) + abs(ny - oy)

        is_u = (nx, ny) in unclaimed
        is_o = (nx, ny) in oppT
        is_s = (nx, ny) in selfT

        gain = 0
        if is_u:
            gain += 3
        elif is_o:
            gain += 5
        elif is_s:
            gain += 1

        # Prefer staying away from the opponent while claiming/pushing forward.
        danger = 0
        if d_o < 5:
            danger += (5 - d_o) * 2
        if d_o < 3:
            danger += (3 - d_o) * 3

        # Slight preference for reducing center distance.
        center_term = -0.15 * d_c

        sc = gain + center_term - danger

        if best is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]