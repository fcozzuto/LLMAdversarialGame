def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    self_role = observation.get("self_role", "pursuer")
    is_pursuer = (self_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = {m: i for i, m in enumerate(moves)}

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Deterministic objective:
    # pursuer: minimize distance, break ties by minimizing turn-away (prefer stable chase) and boundary safety
    # evader: maximize distance, break ties by maximizing escape from pursuer and avoid boundary pinning
    best_val = None
    best_tie = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        # distance improvement relative to current
        cur = d2(sx, sy, ox, oy)
        improv = dist - cur  # negative if closer

        # boundary/obstacle pressure proxy (deterministic)
        near_wall = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        # count blocked neighbors to avoid dead ends
        blocked = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                blocked += 1

        if is_pursuer:
            # lexicographic: prefer smaller dist; then more negative improv; then fewer blocks; then away from wall
            val = dist
            tie = (improv, blocked, 1 if near_wall else 0, order[(dx, dy)])
            better = best_val is None or (val, tie) < (best_val, best_tie)
        else:
            # lexicographic: prefer larger dist; then more positive improv (increase); then fewer blocks; then away from wall
            val = -dist
            tie = (-improv, blocked, 1 if near_wall else 0, order[(dx, dy)])
            better = best_val is None or (val, tie) < (best_val, best_tie)

        if better:
            best_val, best_tie = val, tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]