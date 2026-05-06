def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, 1), (-1, 1), (1, 1)]

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    cx, cy = w // 2, h // 2
    opp_center_d2 = d2(ox, oy, cx, cy)
    self_center_d2 = d2(sx, sy, cx, cy)
    retreat_bias = 1.2 if opp_center_d2 < self_center_d2 else 0.0

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Resource advantage: prefer resources we can reach earlier than opponent.
        res_term = None
        for rx, ry in resources:
            sd = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)
            # Lower is better: prioritize minimal sd and positive advantage (od - sd).
            score = sd - 0.75 * (od - sd)  # becomes smaller when we are advantaged
            if res_term is None or score < res_term:
                res_term = score

        center_pen = retreat_bias * d2(nx, ny, cx, cy)  # retreat from center when opponent is there
        # Small tie-break: prefer moves that slightly increase distance from opponent (avoid collision/contested loops).
        opp_sep = 0.08 * d2(nx, ny, ox, oy)
        move_score = res_term + center_pen - opp_sep

        if best_score is None or move_score < best_score or (move_score == best_score and (dx, dy) < tuple(best_move)):
            best_score = move_score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]