def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance (diagonal steps cost 1)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    # Evaluate next position by best achievable advantage over opponent for any remaining resource.
    best = None
    best_mv = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Prefer resources where we can arrive earlier, but also avoid moving into losing races.
        # Score tuple: (goodness, -self_time, -opp_time, nx, ny) so max goodness then earlier times.
        best_for_pos = None
        for rx, ry in resources:
            sd = cd(nx, ny, rx, ry)
            od = cd(ox, oy, rx, ry)
            # Advantage: positive if we arrive no later than opponent; strongly prefer earlier arrival.
            adv = od - sd
            # Slight bias for resources that are closer (to reduce contention ties deterministically).
            tie_bias = -sd
            cand = (adv, tie_bias, -sd, -od, rx, ry)
            if best_for_pos is None or cand > best_for_pos:
                best_for_pos = cand

        if best is None or best_for_pos > best:
            best = best_for_pos
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]