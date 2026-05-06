def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        cx, cy = w // 2, h // 2
        best_dxdy = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            k = (man(nx, ny, cx, cy), -man(nx, ny, ox, oy), dx, dy)
            if best_key is None or k < best_key:
                best_key = k
                best_dxdy = (dx, dy)
        return [best_dxdy[0], best_dxdy[1]]

    # Score each move by the best resource it could approach, preferring resources
    # we're closer to than the opponent, and keeping some separation.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_opp_sep = -man(nx, ny, ox, oy)  # higher separation => smaller negative
        best_res_key = None
        for rx, ry in resources:
            md = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we can take: (my distance - advantage threshold)
            # Also prefer moving toward nearer resources.
            res_key = (md - 0.6 * od, md + 0.15 * od, abs(rx - nx) + abs(ry - ny))
            if best_res_key is None or res_key < best_res_key:
                best_res_key = res_key

        # Combine: primary is best_res_key, then keep distance to opponent, then deterministic tie-break
        k = (best_res_key[0], best_res_key[1], my_opp_sep, dx, dy)
        if best_key is None or k < best_key:
            best_key = k
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]