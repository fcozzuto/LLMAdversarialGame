def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obs_count = len(obstacles)
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in valid_moves:
            d = cheb(nx, ny, tx, ty)
            key = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_global = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        s_d = cheb(sx, sy, rx, ry)
        o_d = cheb(ox, oy, rx, ry)
        margin = o_d - s_d
        # Prefer resources where we are closer (margin positive), else still pick reasonably close.
        score = margin * 100 - s_d
        if best_global is None or score > best_global[0] or (score == best_global[0] and (s_d, rx, ry) < best_global[1]):
            best_global = (score, (s_d, rx, ry), (rx, ry))

    # Evaluate each move by best achievable margin from its next position, with small second-step penalty.
    chosen = None
    for dx, dy, nx, ny in valid_moves:
        # Block/obstacle proximity penalty: avoid moves that put us adjacent to many obstacles.
        adj = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                ax, ay = nx + ex, ny + ey
                if (ax, ay) in obstacles:
                    adj += 1

        best_move_score = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            s_d = cheb(nx, ny, rx, ry)
            o_d = cheb(ox, oy, rx, ry)
            margin = o_d - s_d
            # small lookahead: consider our ability to stay on a top target after one more step toward it
            tx_step = 0
            best_step = 10**9
            for mdx, mdy in moves:
                nnx, nny = nx + mdx, ny + mdy
                if not inb(nnx, nny) or (nnx, nny) in obstacles:
                    continue
                best_step = min(best_step, cheb(nnx, nny, rx, ry))
            tx_step = best_step
            score = margin * 100 - s_d - (tx_step - s_d) * 2 - adj * (3 + obs_count)
            key = (score, -margin, -s_d, rx, ry, dx, dy)
            if best_move_score is None or key > best_move_score[0]:
                best_move_score