def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    capr = int(observation.get("capture_radius", 0))
    capr2 = capr * capr

    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Fallback if everything blocked
    if not any(valid(sx + dx, sy + dy) for dx, dy in actions):
        return [0, 0]

    # Deterministic tie-breaking: fixed action order
    best_move = [0, 0]
    best_val = None

    # For evader: prefer corners away from opponent; for pursuer: prefer diagonals that reduce distance
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    # Choose an anchor target based on opponent position and deterministically on turn_index
    ti = int(observation.get("turn_index", 0))
    corner_scores = []
    for cx, cy in corners:
        corner_scores.append((dist2(cx, cy, ox, oy), (cx, cy)))
    corner_scores.sort(key=lambda t: (-t[0], t[1][0], t[1][1]))
    anchor = corner_scores[ti % len(corner_scores)][1]

    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        d2 = dist2(nx, ny, ox, oy)
        captured = (d2 <= capr2)

        # Small obstacle pressure: prefer moves with more free surrounding cells
        free = 0
        for adx, ady in actions:
            tx, ty = nx + adx, ny + ady
            if valid(tx, ty):
                free += 1

        if pursuer:
            # Maximize: capture first, then minimize distance, then maximize freedom to avoid getting trapped
            val = (1 if captured else 0, -d2, free)
        else:
            # Maximize: maximize distance, then move toward anchor corner, then maximize freedom
            to_anchor = dist2(nx, ny, anchor[0], anchor[1])
            val = (1 if captured else 0, d2, -to_anchor, free)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move