def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Deterministic corner target (used only as tie-breaker / secondary objective)
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    far_corner = max(corners, key=lambda c: (dist(c[0], c[1], ox, oy), -c[0], -c[1]))
    near_corner = min(corners, key=lambda c: (dist(c[0], c[1], ox, oy), c[0], c[1]))

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_after = dist(nx, ny, ox, oy)

        # Primary objective: maximize survival distance (evader) or chase distance (pursuer)
        primary = d_after if self_is_evader else -d_after

        # Secondary objective: move toward/away from selected corner deterministically
        corner = far_corner if self_is_evader else near_corner
        sec = dist(nx, ny, corner[0], corner[1])

        # Tertiary objective: prefer staying closer to current best axis-aligned direction (stable tie-break)
        stable = (abs(dx) == 1 and abs(dy) == 1)

        # Build a single comparable key (maximize primary, then minimize/maximize sec appropriately, then deterministic tie)
        if self_is_evader:
            key = (primary, -sec, -int(stable), dx, dy)
        else:
            key = (primary, sec, -int(stable), dx, dy)

        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]