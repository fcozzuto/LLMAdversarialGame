def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    # Small deterministic tie-break: prefer staying near center and not hugging edges.
    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine rejects, so treat as staying
        if not resources:
            val = -(abs(nx - center_x) + abs(ny - center_y))
            if val > best_val:
                best_val, best = val, [dx, dy]
            continue

        # Choose the single resource that maximizes our advantage from (nx,ny),
        # with a denial bonus for opponent-row resources (likely sweep_rows behavior).
        local_best = -10**18
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds  # positive if we are closer
            deny = 0
            if ry == oy:
                # If opponent is sweeping along this row, being closer than them matters more.
                deny = 2.5 * adv
            # Mild preference: pick closer resources and avoid edge patrol.
            edge_pen = 0.15 * min(rx, ry, w - 1 - rx, h - 1 - ry)
            val = 3.0 * adv - 0.05 * ds + deny + edge_pen
            if val > local_best:
                local_best = val

        # Global tie-break: prefer center among near-equivalent moves.
        center_bias = -0.02 * (abs(nx - center_x) + abs(ny - center_y))
        total = local_best + center_bias
        if total > best_val:
            best_val, best = total, [dx, dy]

    if best is None:
        best = [0, 0]
    return [int(best[0]), int(best[1])]