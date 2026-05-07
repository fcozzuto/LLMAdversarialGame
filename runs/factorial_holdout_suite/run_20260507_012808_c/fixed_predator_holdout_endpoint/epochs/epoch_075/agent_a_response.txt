def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target resource: prioritize being earlier (opp_d - self_d), then closer.
    # If tie/near-tie, bias toward resources that reduce opponent influence (minimize opp_d).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (od - sd, -sd, -od, -min(od, 1000), rx, ry)
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Weight: when opponent is close to the target, increase denial (move to maximize distance from opponent).
    opp_to_target = md(ox, oy, tx, ty)
    self_to_target = md(sx, sy, tx, ty)
    lam = 2 if opp_to_target <= self_to_target else 1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = md(nx, ny, tx, ty)
        d_from_opp = md(nx, ny, ox, oy)
        # If we already are at target cell, just keep collecting (prefer staying).
        if (sx, sy) == (tx, ty):
            score = (0, -d_from_opp, 0, dx, dy)
        else:
            score = (-(d_to_target), lam * d_from_opp, -(md(nx, ny, tx, ty) + 0.1 * d_from_opp), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]