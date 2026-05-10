def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    role = observation.get("self_role", "pursuer") or "pursuer"
    pursue = (role != "evader")

    best_move = (0, 0)
    best_score = None

    # Preference anchors to reduce dithering: pursue toward opponent, evade toward opposite corner.
    anchor_x, anchor_y = (0, 0) if (sx + sy <= (w - 1) + (h - 1)) else (w - 1, h - 1)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_to_op = manh(nx, ny, ox, oy)
        d_opp = cheb(nx, ny, ox, oy)

        # If capture were possible, pursuer should minimize cheb; evader maximize it.
        primary = -d_opp if pursue else d_opp

        # Secondary: pursue reduce distance; evade increase; then bias toward/away from anchor.
        secondary = (d_to_op if not pursue else -d_to_op)
        anchor_dist = manh(nx, ny, anchor_x, anchor_y)
        tertiary = anchor_dist if not pursue else -anchor_dist

        score = (primary, secondary, tertiary)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # Always return a legal move (or stay).
    return [int(best_move[0]), int(best_move[1])]