def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Consider a small deterministic subset of resources
    res_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    candidates = res_sorted[:6]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = None
    best_score = None

    for dx, dy, nx, ny in moves:
        move_score = -10**9
        for rx, ry in candidates:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; also prefer decreasing our distance
            score = (opp_d - our_d) * 10 - our_d
            # Mild bias to stay progressing away from our start corner and toward opponent side
            score += 0.2 * (cheb(nx, ny, w - 1, h - 1) - cheb(sx, sy, w - 1, h - 1))
            # Avoid hugging obstacles
            adj = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        adj += 1
            score -= adj * 0.8
            if score > move_score:
                move_score = score

        # Tie-break deterministically
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dx, dy, nx, ny)
        elif move_score == best_score:
            # Prefer move that gets closer to opponent (Chebyshev), then toward center
            bx, by, _, _ = best_move
            if cheb(nx, ny, w - 1, h - 1) < cheb(sx + bx, sy + by, w - 1, h - 1):
                best_move = (dx, dy, nx, ny)
            elif cheb(nx, ny, w - 1, h - 1) == cheb(sx + bx, sy + by, w - 1, h - 1):
                if cheb(nx, ny, cx, cy) < cheb(sx + bx, sy + by, cx, cy):
                    best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]