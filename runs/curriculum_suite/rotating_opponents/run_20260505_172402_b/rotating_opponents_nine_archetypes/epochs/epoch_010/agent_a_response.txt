def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def md(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Score each move by its advantage over the opponent on resources,
        # plus a small preference for reducing own distance.
        move_score = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Lead component: positive if we are closer than opponent.
            lead = opd - myd
            # Contestedness: prefer resources that opponent is relatively near.
            contested = (opd <= 6) * 3 + (opd <= 3) * 6
            # Capture bonus if we land on/adjacent (resource may be collected only on landing,
            # but adjacency still helps in typical nearest-resource opponents).
            capture = 10 if (nx == rx and ny == ry) else 0
            # Encourage progressing toward resources without over-penalizing.
            prog = -myd
            sc = lead * 50 + contested * 8 + capture + prog
            if sc > move_score:
                move_score = sc

        # Tie-break deterministically: prefer smaller my distance to best resource area,
        # then lexicographically by move.
        if best is None or move_score > best:
            best = move_score
            best_move = (dx, dy)
        elif move_score == best:
            # Deterministic tie-break using distances sum to closest resource.
            my_near = min(md(nx, ny, rx, ry) for rx, ry in resources)
            cur_near = min(md(sx + best_move[0], sy + best_move[1], rx, ry) for rx, ry in resources)
            if my_near < cur_near or (my_near == cur_near and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]