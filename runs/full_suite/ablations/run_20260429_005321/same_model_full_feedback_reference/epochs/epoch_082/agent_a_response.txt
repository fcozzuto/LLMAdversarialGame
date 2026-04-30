def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If no resources, drift toward the center while also keeping away from obstacles' vicinity.
    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer toward center; small penalty if near obstacle.
            near_obs = 0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    if (nx + ex, ny + ey) in obstacles:
                        near_obs += 1
            score = dist2(nx, ny, cx, cy) + 0.05 * near_obs - 0.001 * dist2(nx, ny, ox, oy)
            cand = (-score, nx, ny, dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[3], best[4]] if best else [0, 0]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate the best resource for this next position using "win-pressure":
        # prefer resources where (op_dist - self_dist) is large (we are closer than opponent).
        # Secondary: prefer nearer resources overall to race pickup; tertiary: stable tie-break.
        best_res_score = None
        for rx, ry in resources:
            sd = dist2(nx, ny, rx, ry)
            od = dist2(ox, oy, rx, ry)
            # If we're already on it, strongly prefer.
            grab = -1000000 if (nx == rx and ny == ry) else 0
            # Higher is better
            score = (od - sd) * 10.0 - sd * 0.05 + grab
            # Tiebreak by coordinates for determinism
            cand_res = (score, -sd, -od, rx, ry)
            if best_res_score is None or cand_res > best_res_score:
                best_res_score = cand_res

        # Also lightly discourage moving farther from opponent if we're not contesting well:
        # helps when near-ties occur.
        od_curr = dist2(nx, ny, ox, oy)
        cand_move = (best_res_score[0], best_res_score[1], best_res_score[2], -od_curr, nx, ny, dx, dy)
        if best is None or cand_move > best:
            best = cand_move

    return [best[6], best[7]] if best else [0, 0]