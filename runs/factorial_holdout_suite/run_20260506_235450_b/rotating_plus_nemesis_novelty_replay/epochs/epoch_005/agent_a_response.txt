def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If no resources visible, drift to a corner that is far from opponent.
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: (dist2(sx, sy, p[0], p[1]), -dist2(ox, oy, p[0], p[1]), p[0], p[1]))
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (dist2(nx, ny, tx, ty), dist2(nx, ny, ox, oy), nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    best_val = None
    best_move = [0, 0]

    # Choose the neighbor cell that maximizes immediate "opponent advantage" toward some resource.
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate best resource for this candidate cell.
        local_best = None
        for rx, ry in resources:
            ds = dist2(nx, ny, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Larger (do - ds) is better; then smaller ds; then deterministic tie-break.
            key = (do - ds, -ds, nx, ny, rx, ry)
            if local_best is None or key > local_best[0]:
                local_best = (key, ds)
        if local_best is None:
            continue
        if best_val is None or local_best[0] > best_val:
            best_val = local_best[0]
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]