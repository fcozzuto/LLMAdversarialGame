def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        ax = abs(x - ox)
        ay = abs(y - oy)
        return ax if ax > ay else ay

    def eval_move(nx, ny):
        d = cheb(nx, ny)
        if is_evader:
            # Prefer increasing distance; avoid trapping near obstacles; encourage cornering only if it increases distance.
            pen_obs = 0
            for bx, by in blocked:
                md = abs(nx - bx) + abs(ny - by)
                if md == 0:
                    pen_obs += 1000
                elif md == 1:
                    pen_obs += 8
                elif md == 2:
                    pen_obs += 3
            # Small bias to edges (for corner evasion archetype), but only via distance.
            edge_bias = (nx in (0, w - 1)) + (ny in (0, h - 1))
            return d * 100 - pen_obs + edge_bias
        else:
            # Pursuer: minimize distance, strongly punish proximity to obstacles.
            pen_obs = 0
            for bx, by in blocked:
                md = abs(nx - bx) + abs(ny - by)
                if md == 0:
                    pen_obs += 1000
                elif md == 1:
                    pen_obs += 20
                elif md == 2:
                    pen_obs += 7
            # Tie-breaker: reduce both axes difference to cut off.
            ax = abs(nx - ox)
            ay = abs(ny - oy)
            return -d * 100 - pen_obs - (ax + ay)

    best_val = None
    best_move = [0, 0]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic order: choose lexicographically among equal evaluations after applying moves list order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = eval_move(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_move = [dx, dy]
    if legal(sx, sy):
        return best_move if best_move != [0, 0] or is_evader else [0, 0]
    # If current cell is somehow blocked, fall back to staying.
    return [0, 0]