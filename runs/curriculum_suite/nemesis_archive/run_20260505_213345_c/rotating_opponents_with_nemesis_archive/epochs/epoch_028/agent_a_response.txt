def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, x, y):
        d = a - x
        if d < 0: d = -d
        e = b - y
        if e < 0: e = -e
        return d + e

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx, dy = x - cx, y - cy
        d = dx * dx + dy * dy
        return d

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Edge_patrol counter: prefer staying/advancing toward interior and keeping distance.
        min_opp = 10**9
        for rx, ry in ((nx, ny),):
            min_opp = min(min_opp, man(ox, oy, rx, ry))

        # Choose a target resource based on best tradeoff: distance to us, and how contested it is by opponent,
        # but also strongly prefer interior resources.
        best_res_val = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            self_d = man(sx, sy, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            cont = 3 * (self_d) - 2 * (opp_d)  # lower is better: closer to us, farther from opponent
            interior = center_bias(rx, ry)
            edge_pen = 0
            if rx == 0 or ry == 0 or rx == w - 1 or ry == h - 1:
                edge_pen = 1000
            # prefer moves that reduce our distance to an interior-leaning, low-contest resource
            val = cont + 0.01 * interior + edge_pen
            if val < best_res_val:
                best_res_val = val

        # Action value: maximize distance from opponent while improving toward interior target.
        toward = min( man(nx, ny, rx, ry) for (rx, ry) in resources )
        val = (best_res_val, toward, -min_opp, center_bias(nx, ny), dx, dy)
        if best is None or val < best[0]:
            best = (val, [dx, dy])

    return best[1] if best is not None else [0, 0]