def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or (role == "pursuer")

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    turn = int(observation.get("turn_index") or 0)
    parity = turn & 1

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)

        if pursuer:
            # Greedy catch: minimize distance; break ties by preferring alignment that reduces both dx and dy when possible.
            align = (abs((nx - ox)) + abs((ny - oy)))  # smaller is better
            score = (-d, -align, nx, ny)
        else:
            # Evasion: maximize distance; additionally bias to move along alternating axis to counter zigzag.
            d_corner = max(cheb(nx, ny, c[0], c[1]) for c in corners)
            step_bias = (abs(dx) > 0) if parity == 0 else (abs(dy) > 0)
            # Prefer moving away from opponent (increase cheb), then maximize corner distance, then bias on axis, then stable tie-break.
            score = (d, d_corner, step_bias, nx, ny)

        # Convert score to a deterministic ordering
        if best is None or score > best_val:
            best = (dx, dy)
            best_val = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]