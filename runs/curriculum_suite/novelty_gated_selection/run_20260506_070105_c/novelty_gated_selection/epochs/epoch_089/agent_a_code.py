def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_dists(px, py):
        if not resources:
            return (10**9, None, 10**9)
        best_my_d = 10**9
        best_op_d = 10**9
        tie_best = None
        for rx, ry in resources:
            d = manh(px, py, rx, ry)
            if d < best_my_d:
                best_my_d = d
                tie_best = (rx, ry)
        for rx, ry in resources:
            if tie_best is not None and (rx, ry) != tie_best:
                continue
            do = manh(ox, oy, rx, ry)
            if do < best_op_d:
                best_op_d = do
        return best_my_d, tie_best, best_op_d

    def move_to_newpos(dx, dy):
        nx, ny = sx + dx, sy + dy
        if (not inb(nx, ny)) or (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = move_to_newpos(dx, dy)
            val = manh(nx, ny, cx, cy) - 0.01 * manh(nx, ny, ox, oy)
            if val < best[0]:
                best = (val, dx, dy)
        return [int(best[1]), int(best[2])]

    _, _, op_near = best_dists(ox, oy)
    best_score = 10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = move_to_newpos(dx, dy)
        my_d, my_tgt, op_d = best_dists(nx, ny)
        # Prefer being closer to a contested target than opponent; also prefer reducing opponent's best distance.
        score = (my_d - op_d) * 100 + my_d * 2 - op_d * 1
        # If we can reach a resource at equal/advantage distance, bias towards immediate pickup region.
        if my_tgt is not None:
            score -= 0.5 * (op_d - op_near)
        # Deterministic tie-break: lexicographic on move.
        if score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]