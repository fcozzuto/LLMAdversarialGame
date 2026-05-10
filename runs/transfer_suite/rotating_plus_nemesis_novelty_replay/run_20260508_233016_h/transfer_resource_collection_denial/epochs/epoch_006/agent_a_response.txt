def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_list)
    if not resources:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Immediate safe pickup
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set and (nx, ny) not in obstacles:
            sc = dist2(nx, ny, ox, oy)
            if best is None or sc < best[0]:
                best = (sc, dx, dy)
    if best is not None:
        return [best[1], best[2]]

    # Choose best target using a deterministic score: prefer resources we are closer to than opponent
    best_target = None
    best_tscore = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        # Higher is better: opponent farther + our closeness
        tscore = (od - sd, -sd, -(abs(rx - sx) + abs(ry - sy)))
        if best_tscore is None or tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target

    # Pick move that advances toward target and (secondarily) increases distance from opponent target race
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = dist2(nx, ny, tx, ty)
        pod = dist2(ox, oy, tx, ty)
        # If we can grab on this move, prioritize strongly
        grab_bonus = 0
        if (nx, ny) in res_set:
            grab_bonus = 10**9
        # Also prefer moves that make opponent "effectively worse" by not approaching them too much
        oppdist = dist2(nx, ny, ox, oy)
        ms = (grab_bonus - nsd + pod * 0, -nsd, oppdist, -(abs(dx) + abs(dy)))
        if best_m is None or ms > best_m[0]:
            best_m = (ms, dx, dy)

    if best_m is None:
        return [0, 0]
    return [best_m[1], best_m[2]]