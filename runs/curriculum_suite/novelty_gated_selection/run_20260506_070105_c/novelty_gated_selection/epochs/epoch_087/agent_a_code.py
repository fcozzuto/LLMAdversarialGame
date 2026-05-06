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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def clamp_to_valid(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = clamp_to_valid(sx + dx, sy + dy)
            dcen = md(nx, ny, cx, cy)
            dop = md(nx, ny, ox, oy)
            key = (dcen, -dop, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Focus on nearest few resources for robustness + speed
    resources_sorted = sorted(resources, key=lambda p: md(sx, sy, p[0], p[1]))
    focus = resources_sorted[:6]

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = clamp_to_valid(sx + dx, sy + dy)

        # Immediate capture consideration
        min_to_res = 10**9
        res_tie = 10**9
        for rx, ry in focus:
            d = md(nx, ny, rx, ry)
            if d < min_to_res:
                min_to_res = d
                res_tie = md(nx, ny, ox, oy)
            elif d == min_to_res:
                # break ties to keep farther from opponent
                dpo = md(nx, ny, ox, oy)
                if dpo > res_tie:
                    res_tie = dpo

        d_op = md(nx, ny, ox, oy)

        # Also penalize stepping into opponent "diagonal probe" by discouraging moves that
        # reduce distance to opponent while not improving resource progress.
        # Use a slight lookahead: compare opponent distance change.
        d_op_now = md(sx, sy, ox, oy)
        d_op_delta = d_op_now - d_op  # positive if we move closer to opponent

        # Score: prefer closer resource; then prefer farther from opponent; then avoid approaching opponent.
        key = (min_to_res, -d_op, d_op_delta, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]