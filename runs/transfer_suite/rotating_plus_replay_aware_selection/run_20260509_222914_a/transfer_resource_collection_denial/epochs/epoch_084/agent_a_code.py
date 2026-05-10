def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_move = [0, 0]
    best_score = None
    best_tiebreak = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        move_best = None
        move_self_best = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Prefer resources we are closer to than the opponent; also slightly penalize overall distance.
            score = (do - ds) - 0.1 * ds
            if move_best is None or score > move_best or (score == move_best and ds < move_self_best):
                move_best = score
                move_self_best = ds

        if move_best is None:
            continue

        if best_score is None or move_best > best_score:
            best_score = move_best
            best_move = [dx, dy]
            best_tiebreak = move_self_best
        elif move_best == best_score:
            # Deterministic tie-break: closer to chosen resource; then prefer staying/straight over diagonal.
            if move_self_best < best_tiebreak:
                best_move = [dx, dy]
                best_tiebreak = move_self_best
            elif move_self_best == best_tiebreak:
                # prefer [0,0], then straight, then diagonal
                curr_diag = 1 if dx != 0 and dy != 0 else 0
                curr_stay = 1 if dx == 0 and dy == 0 else 0
                best_dx, best_dy = best_move
                best_diag = 1 if best_dx != 0 and best_dy != 0 else 0
                best_stay = 1 if best_dx == 0 and best_dy == 0 else 0
                if curr_stay > best_stay or (curr_stay == best_stay and curr_diag < best_diag):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]