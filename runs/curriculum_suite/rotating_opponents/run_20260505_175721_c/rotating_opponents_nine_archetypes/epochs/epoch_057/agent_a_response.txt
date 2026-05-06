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

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    def best_target():
        best = None
        for tx, ty in resources:
            sd = md(sx, sy, tx, ty)
            od = md(ox, oy, tx, ty)
            # Heuristic: prefer resources we can reach sooner; break ties by closeness.
            # Small center bias to reduce pathing loops once resources thin.
            center_bias = -0.02 * md(tx, ty, (w - 1) // 2, (h - 1) // 2)
            val = (od - sd + center_bias, -sd, tx, ty)
            if best is None or val > best:
                best = val
        return None if best is None else (best[2], best[3])

    target = best_target()
    cx, cy = (w - 1) // 2, (h - 1) // 2
    tx, ty = target if target is not None else (cx, cy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Next-step evaluation: stay competitive against opponent and continue toward target.
        nsd = md(nx, ny, tx, ty)
        nod = md(nx, ny, ox, oy)
        sdist = md(nx, ny, tx, ty)
        odist = md(ox, oy, tx, ty)
        # Prefer decreasing our distance to target; also prefer moves that reduce opponent-to-target advantage.
        score = (-(sdist), (odist - sdist), -nod * 0.001, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]