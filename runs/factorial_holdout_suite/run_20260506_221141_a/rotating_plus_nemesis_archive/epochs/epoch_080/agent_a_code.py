def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def mdist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_resource():
        best = None
        best_val = None
        for rx, ry in resources:
            sd = mdist(sx, sy, rx, ry)
            od = mdist(ox, oy, rx, ry)
            # Higher is better: prioritize grabbing before opponent, then nearer.
            # Tie-break: prefer resources closer to opponent if we can still deny (smaller od).
            val = (od - sd, -sd, -od, -rx, -ry)
            if best_val is None or val > best_val:
                best_val = val
                best = (rx, ry)
        return best

    target = best_resource()
    tx, ty = target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_dir_bias = (1 if ox < sx else -1 if ox > sx else 0, 1 if oy < sy else -1 if oy > sy else 0)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target; Secondary: avoid moving into opponent's immediate race line.
        sd_new = mdist(nx, ny, tx, ty)
        sd_old = mdist(sx, sy, tx, ty)
        step_progress = sd_old - sd_new

        # Race value against best resource (recomputed simply for the chosen target).
        od = mdist(ox, oy, tx, ty)
        # Approx our advantage after move
        race_adv = (od - sd_new)

        # Small deterministic penalty if we "mirror" toward opponent (helps prevent over-commit into deniers)
        mirror_pen = (dx != 0 and opp_dir_bias[0] != 0 and dx == opp_dir_bias[0]) or (dy != 0 and opp_dir_bias[1] != 0 and dy == opp_dir_bias[1])
        mirror_pen = 1 if mirror_pen else 0

        score = (race_adv, step_progress, -sd_new, -nx, -ny, -mirror_pen)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]