def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    if "evader" in self_role:
        mode = "evade"
    elif "pursuer" in self_role:
        mode = "pursue"
    else:
        scores = observation.get("scores") or {}
        my_s = 0.0
        op_s = 0.0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0.0))) or 0.0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0.0))) or 0.0
        mode = "evade" if float(my_s) >= float(op_s) else "pursue"

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    candidates = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # deterministic tie-breaking preference: towards staying (0,0), then lexicographic dx,dy
    def sort_key(item):
        dx, dy, nx, ny = item
        return (abs(dx) + abs(dy), 0 if (dx == 0 and dy == 0) else 1, dx, dy)

    best = None
    best_score = None
    for dx, dy, nx, ny in sorted(candidates, key=sort_key):
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        step2 = dx * dx + dy * dy
        # obstacle handling: lookahead penalty if opponent can "see" tight corner next
        # (simple local measure: penalize moving into adjacent obstacle cells)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj_obs += 1

        # prefer evasion: maximize dist2; prefer pursuit: minimize dist2
        # also discourage hard moves unless they improve distance, to avoid boundary rejections.
        if mode == "evade":
            score = dist2 - 0.15 * step2 - 0.5 * adj_obs
        else:
            score = -dist2 - 0.15 * step2 - 0.5 * adj_obs

        if best is None:
            best, best_score = (dx, dy), score
        else:
            better = score > best_score if mode == "evade" else score > best_score
            if better:
                best, best_score = (dx, dy), score

    return [int(best[0]), int(best[1])]