def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    obs = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            try:
                obs.add((int(b[0]), int(b[1])))
            except:
                pass

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def valid(nx, ny):
        return inb(nx, ny) and not blocked(nx, ny)

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Simple "escape direction" bias toward farthest corner when evading
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    candidates = []
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        d = dist2(nx, ny, ox, oy)

        # Evaluate local maneuver safety: avoid being squeezed (min free neighbors)
        free_n = 0
        for adx, ady in actions:
            tx, ty = nx + adx, ny + ady
            if valid(tx, ty):
                free_n += 1

        if pursuer:
            # Also discourage staying in place when it doesn't improve distance.
            score = (-d, free_n, -abs(ox - nx) - abs(oy - ny))
        else:
            # Evade: maximize distance, bias toward a corner and toward higher mobility.
            target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
            corner_bias = -dist2(nx, ny, target_corner[0], target_corner[1])
            score = (d, free_n, corner_bias)

        candidates.append((score, (dx, dy)))

    # Deterministic tie-break: lexicographic on (dx,dy) after score
    if pursuer:
        best_score = None
        best_move = (0, 0)
        for score, mv in candidates:
            if best_score is None or score > best_score or (score == best_score and mv < best_move):
                best_score, best_move = score, mv
    else:
        best_score = None
        best_move = (0, 0)
        for score, mv in candidates:
            if best_score is None or score > best_score or (score == best_score and mv < best_move):
                best_score, best_move = score, mv

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]