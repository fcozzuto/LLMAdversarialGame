def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                unclaimed.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    targets = unclaimed
    if not targets:
        targets = [(ox, oy)]
    tcx, tcy = None, None
    bestd = None
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if bestd is None or d < bestd or (d == bestd and (x, y) < (tcx, tcy)):
            bestd = d
            tcx, tcy = x, y

    cx, cy = w // 2, h // 2
    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        dist_to_target = abs(tcx - nx) + abs(tcy - ny)
        dist_to_center = abs(cx - nx) + abs(cy - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        score = (-dist_to_target * 10) + (-dist_to_center) + (dist_to_opp if not unclaimed else 0) + (-dx * 0 + dy * 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move