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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # Deterministic fallback: drift toward the center while keeping distance from opponent.
        tx, ty = (w // 2), (h // 2)
    else:
        # New targeting: choose the resource where we have the largest immediate advantage in reach.
        # Advantage = opponent_dist - our_dist (bigger is better). Tie-break by being closer to center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_key = None
        for rx, ry in resources:
            myd = dist2(sx, sy, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            adv = opd - myd
            center_pen = dist2(rx, ry, cx, cy)
            # If advantage is small, still prefer slightly off-center to avoid mirror contests.
            key = (adv, -center_pen, -((rx + ry) & 1))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # One-step lookahead: score moves by improving our closeness more than the opponent's, and avoid obstacles.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = dist2(nx, ny, tx, ty)
        opd = dist2(ox, oy, tx, ty)
        # Prefer larger advantage after the move; encourage reducing our distance and slightly increase distance from opponent.
        adv_after = opd - myd
        opp_sep = dist2(nx, ny, ox, oy)
        # Repel from obstacles near destination square (local penalty).
        local_obst = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                px, py = nx + ddx, ny + ddy
                if (px, py) in obstacles:
                    local_obst += 1
        score = 1000 * adv_after + 3 * opp_sep - 20 * local_obst - myd
        # Deterministic tiebreaker: favor moves with smaller (dx,dy) lexicographically after score.
        tiebreak = (dx != 0, dy != 0, dx, dy)
        if score > best_score or (score == best_score and tiebreak < (best_move[0] != 0, best_move[1] != 0, best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]