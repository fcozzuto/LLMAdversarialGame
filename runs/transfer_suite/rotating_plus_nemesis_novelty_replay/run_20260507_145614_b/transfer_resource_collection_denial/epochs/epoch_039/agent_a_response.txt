def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((sx == r[0] and sy == r[1]) for r in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0, 10**9)
        for dx, dy, nx, ny in moves:
            d = cheb(nx, ny, tx, ty)
            if d < best[2]:
                best = (dx, dy, d)
        return [best[0], best[1]]

    best_move = moves[0]
    best_val = -10**18

    # Race heuristic: prefer resources where we reduce opponent lead and keep good absolute proximity.
    for dx, dy, nx, ny in moves:
        val = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Winning race if myd <= opd; emphasize narrowing the gap and closeness.
            race = (opd - myd)
            closeness = -myd
            # Small tie-break toward resources closer to center (more likely next).
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)) * 0.01
            score = race * 10.0 + closeness + center_bias
            if score > val:
                val = score
        if val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]