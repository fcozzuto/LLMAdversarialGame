def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def min_dist(x, y, ax, ay):
        return abs(x - ax) + abs(y - ay)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    # Deterministic tie-break: fixed move order and stable scoring.
    best = None
    best_move = [0, 0]

    d_cur = min_dist(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d_nxt = min_dist(nx, ny, ox, oy)
        step_gain = d_cur - d_nxt  # positive if getting closer (pursuer) or farther (evader) depending on sign

        # Estimate "approach advantage": whether we are moving toward/away in x/y separately (reduces zigzag dithering).
        vx = (ox - nx)
        vy = (oy - ny)
        adv = (1 if vx > 0 else (-1 if vx < 0 else 0)) + (1 if vy > 0 else (-1 if vy < 0 else 0))
        # For evader, prefer moving to reduce this "toward" indicator by maximizing distance; for pursuer, opposite.

        mob = mobility(nx, ny)
        ed = edge_dist(nx, ny)

        if is_evader:
            # Maximize distance, maintain mobility, and avoid hugging edges.
            score = (1000 * d_nxt) + (10 * mob) + (3 * ed) - (2 * abs(dx) + abs(dy)) - (5 * adv)
        else:
            # Minimize distance; prefer moves that reduce distance immediately, keep mobility, and avoid being trapped by edges/obstacles.
            score = (-1000 * d_nxt) + (8 * mob) + (2 * ed) + (2 * step_gain) + (5 * adv)

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]