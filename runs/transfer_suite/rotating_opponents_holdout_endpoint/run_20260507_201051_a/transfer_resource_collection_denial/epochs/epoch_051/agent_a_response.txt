def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev

    # Pick best resource by reach advantage over opponent, then proximity.
    best = None
    best_key = None
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        key = (od - sd, -sd, -(r[0] + r[1]))
        if best_key is None or key > best_key:
            best_key = key
            best = r
    tx, ty = best

    # Evaluate immediate moves (including staying), avoid obstacles, aim for target,
    # and slightly prefer moves that don't give the opponent immediate access.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    prefer_order = {}
    for i, m in enumerate(moves):
        prefer_order[m] = i

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = None
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Target progress and safety margin from opponent.
        d_to_t = dist((nx, ny), (tx, ty))
        d_to_o = dist((nx, ny), (ox, oy))

        # Opponent "threat" to the target from its current position.
        opp_d_to_t = dist((ox, oy), (tx, ty))
        # If we get as close as or closer than opponent, prioritize heavily.
        lead = opp_d_to_t - d_to_t

        # Tie-break: prefer moves that reduce distance to opponent less (i.e., keep distance).
        key = (lead, -d_to_t, d_to_o, -prefer_order[(dx, dy)])
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]