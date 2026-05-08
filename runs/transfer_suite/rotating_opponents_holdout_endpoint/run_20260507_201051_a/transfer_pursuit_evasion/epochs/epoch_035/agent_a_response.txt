def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy
    def edge_margin(x, y): return min(x, y, w - 1 - x, h - 1 - y)

    best_score = -10**30
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in obs:
            continue

        dcur = dist2(sx, sy)
        dnew = dist2(nx, ny)

        if i_am_evader:
            # Run away, prefer perimeter, and avoid moving into tight "approach traps"
            # by lightly discouraging moves that reduce distance too much.
            score = (dnew - dcur) + 0.08 * edge_margin(nx, ny)
            # If distance doesn't increase, add penalty to beat zigzag evasion mistakes.
            if dnew <= dcur:
                score -= 0.25 + 0.001 * dnew
        else:
            # Pursuer: greedily minimize distance, but avoid risky low-mobility squares.
            # Prefer moves that also increase our edge margin slightly (less maneuvering).
            score = -(dnew) + 0.01 * edge_margin(nx, ny)

        # Deterministic tie-break: favor earlier move in moves list via strict '>' only.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]