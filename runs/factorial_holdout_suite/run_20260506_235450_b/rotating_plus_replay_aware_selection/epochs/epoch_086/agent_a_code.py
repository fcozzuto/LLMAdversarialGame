def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Value of choosing a resource from a position: prefer getting it first, then closeness.
    def best_value(px, py):
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d_self = dist(px, py, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            margin = d_opp - d_self  # positive if we arrive earlier
            # Deterministic tiebreak: also prefer resources with smaller (rx+ry) if equal score.
            fav = 1000 if margin > 0 else 0
            score = fav + margin - 0.01 * (d_self) - 0.001 * (rx + ry)
            if best is None or score > best:
                best = score
        return best

    # If our move can pick up a resource immediately, it will naturally rank highest via d_self=0.
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in legal:
        val = best_value(nx, ny)
        # Extra safety: avoid stepping "toward" opponent if no favorable resource is available.
        # (If val is already high, this won't hurt much.)
        d_self_to_opp = dist(nx, ny, ox, oy)
        d_curr_to_opp = dist(sx, sy, ox, oy)
        penalty = 0.1 * (d_self_to_opp - d_curr_to_opp)
        score = val - penalty
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]