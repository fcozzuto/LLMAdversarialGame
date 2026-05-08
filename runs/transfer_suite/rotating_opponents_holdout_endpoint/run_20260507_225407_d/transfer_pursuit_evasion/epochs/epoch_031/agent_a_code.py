def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("escape" in self_role)
    is_pursuer = ("pursuer" in self_role) or ("pursue" in self_role) or ("pursuit" in self_role)
    if not is_evader and not is_pursuer:
        is_evader = ("evader" in opp_role) or ("evasion" in opp_role) or ("escape" in opp_role)
        is_pursuer = not is_evader
    evader_turn = is_evader and not is_pursuer

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If self is pursuer, we move to reduce distance to opponent; otherwise move to increase.
    # Distance: Chebyshev (good for diagonal zigzags).
    def dist(x, y):
        return max(abs(x - ox), abs(y - oy))

    # Deterministic move ordering (prefers forward-like moves over staying).
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # For evasion, also bias toward the farthest corner from the opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: max(abs(c[0] - ox), abs(c[1] - oy)))
    fx, fy = far_corner
    def corner_score(x, y):
        return -max(abs(fx - x), abs(fy - y))  # closer to far corner is better for evader

    best_move = [0, 0]
    if evader_turn:
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = dist(nx, ny) * 10 + corner_score(nx, ny)
            if best_val is None or v > best_val:
                best_val = v
                best_move = [dx, dy]
    else:
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer reducing distance, and also avoid moving onto immediate obstacle-adjacent "traps" slightly.
            v = -dist(nx, ny) * 10
            # Tie-break: move that aligns toward opponent more directly.
            v += -(abs((nx - sx)) + abs((ny - sy)) == 0) * 0.01
            if best_val is None or v > best_val:
                best_val = v
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]