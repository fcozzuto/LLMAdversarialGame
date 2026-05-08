def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            return int(p[0]), int(p[1])
        return None

    obstacles = set()
    for p in observation.get("obstacles") or []:
        q = norm_pos(p)
        if q is not None:
            obstacles.add(q)

    unclaimed = list(observation.get("unclaimed_cells") or [])
    if not unclaimed:
        unclaimed = list(observation.get("opponent_territory") or [])
    targets = []
    for p in unclaimed:
        q = norm_pos(p)
        if q is not None and q not in obstacles:
            targets.append(q)
    if not targets:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18
    tie = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        # Negative distance => closer is better. Add slight preference to avoid getting too close.
        best_target_d = None
        for tx, ty in targets:
            dd = abs(tx - nx) + abs(ty - ny)
            if best_target_d is None or dd < best_target_d:
                best_target_d = dd
        if best_target_d is None:
            continue
        score = -best_target_d + 0.02 * min(30, d_to_opp)
        if score > bestv or (score == bestv and tie is not None and (dx, dy) < tie):
            bestv = score
            best = (dx, dy)
            tie = (dx, dy)

    return list(best) if best is not None else [0, 0]