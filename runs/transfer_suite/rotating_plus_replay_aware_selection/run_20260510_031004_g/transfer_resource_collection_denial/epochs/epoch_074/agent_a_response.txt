def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Score a target: prioritize resources we can reach first; otherwise, deny by targeting the best "race threat".
    best = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        margin = opp_d - my_d  # positive means I arrive not later than opponent
        # If margin>0, strongly prefer; if not, prefer minimizing opponent arrival time and my distance.
        win_bias = 1000 if margin > 0 else 0
        val = win_bias + margin * 10 - my_d
        # Deterministic tie-break: prefer higher rx, then higher ry (stable across turns).
        key = (val, rx, ry, -my_d)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Choose move that reduces chebyshev distance to target while avoiding obstacles; deterministic neighbor order.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_td = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        td = cheb(nx, ny, tx, ty)
        if best_td is None or td < best_td or (td == best_td and (dx, dy) < best_move):
            best_td = td
            best_move = (dx, dy)

    # If all moves blocked, stay.
    if best_td is None:
        return [0, 0]
    return [best_move[0], best_move[1]]