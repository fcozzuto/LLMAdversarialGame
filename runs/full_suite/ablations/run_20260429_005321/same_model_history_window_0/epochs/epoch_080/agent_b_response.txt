def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    # Pick a target resource favoring ones we can reach at least as well as opponent.
    best = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        ds = dist2(sx, sy, rx, ry)
        do = dist2(ox, oy, rx, ry)
        # Prefer resources closer to us; if opponent also close, prefer the one where we are closer.
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_self = dist2(nx, ny, tx, ty)
        d_opp = dist2(ox, oy, tx, ty)
        # Main: move to reduce distance to target.
        # Secondary: prefer targets opponent is farther from (potential contest).
        # Tertiary: avoid getting stuck (prefer not moving away from target).
        cur_d = dist2(sx, sy, tx, ty)
        score = (-d_self, d_opp, -(d_self - cur_d), abs(dx) + abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]