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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_t = None
        best_s = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer being closer than opponent; also prefer not being on opponent's sweep alignment.
            align_pen = 0
            if ry == oy:  # same row as opponent: likely to get swept
                align_pen += 6
            if rx == ox:  # same col: also vulnerable
                align_pen += 2
            # Prefer midboard slightly (avoid hugging edges where sweep can trap).
            mid_bonus = (w // 2 - abs(rx - (w - 1) / 2)) * 0.05 + (h // 2 - abs(ry - (h - 1) / 2)) * 0.05
            sc = (do - ds) - 0.6 * ds + mid_bonus - align_pen
            if best_s is None or sc > best_s or (sc == best_s and (rx, ry) < best_t):
                best_s = sc
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Evaluate next step locally with a "stay away from opponent sweep lines" bias.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)

        # If opponent is aligned, bias to move off that alignment.
        row_sep = abs(ny - oy)
        col_sep = abs(nx - ox)
        align_avoid = 0
        if ny == oy:
            align_avoid += 8
        if nx == ox:
            align_avoid += 4

        # Also discourage stepping closer to opponent when resources are sparse.
        sparse = 1 if not resources else 0
        val = 3.2 * d_to_o - 1.1 * d_to_t - 1.0 * align_avoid - sparse * 0.9 * (man(nx, ny, ox, oy) - man(sx, sy, ox, oy))

        # Tie-break deterministically: prefer smaller dx, then smaller dy.
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]