def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Candidate targets: closest few to us
    scored = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            d = abs(rx - sx) + abs(ry - sy)
            scored.append((d, rx, ry))
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    candidates = scored[:3]

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate against targets, choosing the best "advantage" deterministically
        move_best = None
        for _, tx, ty in candidates:
            my_d = abs(tx - nx) + abs(ty - ny)
            op_d = abs(tx - ox) + abs(ty - oy)

            # Prefer (1) making us closer to a target, (2) keeping opponent farther,
            # (3) when we're not the closest, try to reduce the gap.
            # Tie-break with direction and deterministic stability.
            val = (my_d, op_d, 0 if (my_d <= op_d) else (my_d - op_d), abs(dx) + abs(dy), dx, dy)
            if move_best is None or val < move_best[0]:
                move_best = (val, tx, ty)

        if move_best is None:
            continue

        # Also reward staying near targets that are not already "claimed" by opponent.
        _, tx, ty = move_best
        my_curr = abs(tx - nx) + abs(ty - ny)
        op_curr = abs(tx - ox) + abs(ty - oy)
        val2 = (move_best[0][0], op_curr - my_curr, my_curr, dx, dy)

        if best_val is None or val2 < best_val:
            best_val = val2
            best_move = [dx, dy]

    return best_move