def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = None

    # Deterministic tie-break order for moves
    order = {d: i for i, d in enumerate(dirs)}

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Align with opponent's sweep line (same row or column after the move).
        align_bonus = 3 if (nx == ox or ny == oy) else 0

        # Choose the resource that I can contest best from this next cell.
        # Key prefers: big distance advantage (opp closer => bad), then small my distance,
        # then contest on aligned resources.
        best_r = None
        best_r_key = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # If opponent is closer, still allow contest by preferring resources
            # that are aligned with our move line (same row/col as resource).
            aligned_r = 1 if (rx == ox or ry == oy or nx == rx or ny == ry) else 0
            # Advantage: positive if I am closer or equal.
            adv = opd - myd

            key = (adv, aligned_r, -myd, -opd)
            if best_r_key is None or key > best_r_key:
                best_r_key = key
                best_r = (rx, ry, myd, opd)

        rx, ry, myd, opd = best_r
        # Overall key for move: maximize (adv + align), then minimize my distance,
        # then minimize opponent distance (so I'm the one who takes first).
        move_key = (best_r_key[0] + align_bonus, best_r_key[2], -best_r_key[3], -order[(dx, dy)])
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = [dx, dy]

    return best_move