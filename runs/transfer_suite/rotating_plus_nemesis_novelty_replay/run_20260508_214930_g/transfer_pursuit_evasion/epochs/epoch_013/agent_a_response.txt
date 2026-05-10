def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            try:
                obs.add((int(b[0]), int(b[1])))
            except:
                pass

    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def next_pos(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            return x, y
        return nx, ny

    # Predict: opponent tends to zigzag by moving away from us; target one step away from our position.
    away_dx = ox - sx
    away_dy = oy - sy
    step_x = 0 if away_dx == 0 else (1 if away_dx > 0 else -1)
    step_y = 0 if away_dy == 0 else (1 if away_dy > 0 else -1)
    tx, ty = ox + step_x, oy + step_y
    if not inb(tx, ty) or blocked(tx, ty):
        tx, ty = ox, oy  # fallback

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in actions:
        nsx, nsy = next_pos(sx, sy, dx, dy)
        # Two-term deterministic heuristic: chase predicted target first, then opponent.
        score = dist2(nsx, nsy, tx, ty) * 4 + dist2(nsx, nsy, ox, oy)
        # Small tie-break: prefer moves that progress (reduce distance to opponent).
        score += (dist2(sx, sy, ox, oy) - dist2(nsx, nsy, ox, oy)) * 0.1
        if best is None or score < best_score:
            best_score = score
            best = [dx, dy]

    # If somehow no best (shouldn't), stay.
    if best is None:
        best = [0, 0]
    return best