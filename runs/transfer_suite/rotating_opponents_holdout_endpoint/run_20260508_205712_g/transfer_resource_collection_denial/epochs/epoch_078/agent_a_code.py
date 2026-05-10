def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def step_to(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    if not resources:
        # Two-corner drift: go toward the corner that is farther from opponent (to contest center path less)
        corners = [(0, 0), (0, H - 1), (W - 1, 0), (W - 1, H - 1)]
        tx, ty = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))  # pick where opponent is less likely to go
        dx, dy = step_to(tx, ty)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
        # fallback: best valid move toward tx,ty
        best = None
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if not inb(nx, ny):
                continue
            key = (man(nx, ny, tx, ty), mdx, mdy)
            if best is None or key < best[0]:
                best = (key, [mdx, mdy])
        return best[1] if best is not None else [0, 0]

    # Select resource with strongest "lead" (I am closer than opponent); tie-break by my distance then coordinate order.
    best_res = None
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        op_d = man(ox, oy, rx, ry)
        lead = op_d - my_d  # bigger => I am closer
        if best_res is None:
            best_res = (lead, my_d, rx, ry)
        else:
            cand = (lead, -my_d, rx, ry)  # prefer larger lead; then closer my_d
            cur = (best_res[0], -best_res[1], best_res[2], best_res[3])
            if cand[0] > cur[0] or (cand[0] == cur[0] and cand[1] > cur[1]) or (cand == cur and (rx, ry) < (best_res[2], best_res[3])):
                best_res = (lead, my_d, rx, ry)
    _, _, tx, ty = best_res

    # Move: try greedy toward target; if blocked, choose among valid moves the one minimizing (distance to target, -lead after step).
    dx, dy = step_to(tx, ty)
    if inb(sx + dx, sy + dy):
        return [dx, dy]

    best_move = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        my_d2 = man(nx, ny, tx, ty)
        op_d_now = man(ox, oy, tx, ty)
        # Prefer moves that improve relative lead even if slightly worse by absolute distance
        score = (my_d2, -((op_d_now - my_d2)), mdx, mdy)
        if best_move is None or score < best_move[0]:
            best_move = (score, [mdx, mdy])
    return best_move[1] if best_move is not None else [0, 0]