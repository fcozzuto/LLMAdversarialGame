def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turns_remaining = int(observation.get("turns_remaining") or 0)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # prioritize resources we can reach first; otherwise prefer those where we still "close the gap" sooner
        key = (1 if sd <= od else 0, od - sd, -(sd), -(rx + ry))
        if best_target is None or key > best_key:
            best_target = (rx, ry)
            best_key = key

    tx, ty = best_target
    dist_to = md(sx, sy, tx, ty)
    opp_dist_to = md(ox, oy, tx, ty)
    i_win = 1 if dist_to <= opp_dist_to else 0

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = md(nx, ny, tx, ty)
            nod = md(nx, ny, ox, oy)
            # If opponent is closer to target, try to pull away while still progressing; else maximize progress.
            v_adv = (opp_dist_to - dist_to)  # current advantage sign
            if i_win:
                val = (-nd, nod, -abs((tx - nx) + (ty - ny)), dx, dy)
            else:
                val = (-nd + 0.6 * (nod), -(nd), -nod, dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move