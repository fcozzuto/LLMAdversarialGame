def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    unclaimed = observation.get("unclaimed_cells") or []
    if unclaimed:
        best_t = None
        best_key = None
        for x, y in unclaimed:
            x, y = int(x), int(y)
            if (x, y) in blocked:
                continue
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            # Prefer cells we can reach before/at opponent; otherwise still allow if close.
            reach_adv = do - ds
            k = (-reach_adv, ds, abs(y - (h // 2)), abs(x - (w // 2)))
            if best_key is None or k < best_key:
                best_key = k
                best_t = (x, y)
        tx, ty = best_t if best_t is not None else (w // 2, h // 2)
    else:
        tx, ty = (w // 2, h // 2)

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        ds = abs(nx - tx) + abs(ny - ty)
        # If we move adjacent to opponent, slightly prefer staying safer unless it also improves toward target.
        adj = max(abs(nx - ox), abs(ny - oy))
        opp_pen = 0 if adj >= 2 else (3 - adj)
        # Discourage entering opponent territory if opponent is close (still allow if it is best for reaching target).
        opp_cells = set(map(tuple, observation.get("opponent_territory") or []))
        opp_enter = 1 if (nx, ny) in opp_cells and adj <= 1 else 0
        val = (ds + opp_pen + 4 * opp_enter, abs(nx - tx), abs(ny - ty), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]