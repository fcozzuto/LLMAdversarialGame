def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: lexicographic by dx then dy.
    dirs = sorted(dirs, key=lambda t: (t[0], t[1]))

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # If any corner is blocked, still allow moving toward it; only move legality is enforced.
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        target = (tx, ty)
    else:
        target = (ox, oy)

    best = (None, None, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_target = cheb(nx, ny, target[0], target[1])
        d_to_opp = cheb(nx, ny, ox, oy)
        # Evader wants to maximize distance from pursuer; pursuer wants to minimize.
        primary = d_to_opp if is_evader else -d_to_opp
        # Tie-break: closer to chosen target for evader; for pursuer also closer to opponent.
        secondary = -d_to_target if is_evader else -d_to_target
        score = (primary, secondary)
        if best[0] is None or score > best[0]:
            best = (score, dx, dy)

    if best[1] is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]