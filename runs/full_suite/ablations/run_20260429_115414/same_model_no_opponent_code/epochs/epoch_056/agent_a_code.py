def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cd(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        best = (0, 0)
        best_sc = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            sc = -(cd((nx, ny), (w - 1, h - 1)) + cd((nx, ny), (0, 0)))
            if sc > best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]]

    me = (sx, sy)
    opp = (ox, oy)
    best_r = resources[0]
    best_val = None
    for r in resources:
        my_d = cd(me, r)
        op_d = cd(opp, r)
        # Prefer resources we are closer to; then closer overall; then deterministic by coords.
        val = (my_d - op_d, my_d, r[0], r[1])
        if best_val is None or val < best_val:
            best_val = val
            best_r = r

    tx, ty = best_r
    cur_diff = cd(me, best_r) - cd(opp, best_r)

    best_move = (0, 0)
    best_sc = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        new_me = (nx, ny)
        my_d = cd(new_me, best_r)
        op_d = cd(opp, best_r)
        new_diff = my_d - op_d

        # Strongly drive toward target; slightly prefer improving relative closeness to opponent.
        sc = -my_d * 10 - abs(new_diff) * 2 - new_me[0] * 0.0001 - new_me[1] * 0.0002
        if new_diff < cur_diff:
            sc += 2

        if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]