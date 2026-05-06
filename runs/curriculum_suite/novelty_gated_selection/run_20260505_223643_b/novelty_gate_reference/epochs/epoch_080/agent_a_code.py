def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Evaluate each possible next position: choose the move whose best target favors us (or hurts the opponent less).
    best_move = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        best_for_move = None
        for rx, ry in resources:
            dw = dist_cheb(nx, ny, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            # Prefer being no slower; otherwise penalize being slower more when opponent can be much faster.
            if dw <= do:
                cand = (0, dw, do, abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            else:
                lead = do - dw
                cand = (1, dw + 3 * lead, do, abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            if best_for_move is None or cand < best_for_move:
                best_for_move = cand

        # If target pressure is similar, prefer increasing distance from opponent (robust vs diagonal probes).
        opp_sep = dist_cheb(nx, ny, ox, oy)
        move_key = (best_for_move[0], best_for_move[1], -opp_sep, best_for_move[3], dxm, dym)
        if best_move is None or move_key < best_move[0]:
            best_move = (move_key, dxm, dym)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]