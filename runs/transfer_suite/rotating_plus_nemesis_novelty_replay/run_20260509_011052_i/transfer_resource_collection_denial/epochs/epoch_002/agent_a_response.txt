def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)

    sp = observation.get('self_position', (0, 0))
    op = observation.get('opponent_position', (0, 0))
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obstacles = observation.get('obstacles', []) or []
    obs = set()
    for p in obstacles:
        if len(p) >= 2:
            obs.add((p[0], p[1]))

    resources = observation.get('resources', []) or []

    if resources:
        best = None
        for r in resources:
            if len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            myd = abs(rx - sx) + abs(ry - sy)
            opd = abs(rx - ox) + abs(ry - oy)
            # Favor resources where we are closer; strongly avoid being beaten badly.
            score = myd - 0.9 * opd
            # Tie-break deterministically: lower myd, then lower coordinates
            key = (score, myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = w // 2, h // 2

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))

    # Always include staying as last resort (even if obstacle somehow blocks current pos)
    if (0, 0) not in moves:
        moves.append((0, 0))

    # Evaluate moves by progress toward target, and threat from opponent
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        myd = abs(tx - nx) + abs(ty - ny)
        opd = abs(tx - ox) + abs(ty - oy)
        # If we move onto a resource (or closer), myd decreases; also consider contention.
        key = (myd - 0.6 * opd, abs(ox - nx) + abs(oy - ny), nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]