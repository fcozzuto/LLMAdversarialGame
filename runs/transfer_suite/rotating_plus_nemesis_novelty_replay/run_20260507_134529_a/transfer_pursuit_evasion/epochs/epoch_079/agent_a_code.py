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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evader: run to farthest safe corner; Pursuer: minimize distance with a small obstacle-aware tie-break.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        # Prefer corner that maximizes distance from opponent; if current corner blocked, still compare by distance.
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy) + (0 if (c[0], c[1]) in obstacles else 1))
    else:
        tx, ty = ox, oy

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Main objective: approach target if pursuer, flee from opponent if evader.
        if is_evader:
            primary = cheb(nx, ny, ox, oy)
            # Secondary: also move toward chosen corner (negative distance so it prefers smaller).
            secondary = cheb(nx, ny, tx, ty)
        else:
            primary = cheb(nx, ny, ox, oy)
            # Secondary: prefer fewer "dead-end" moves (more mobility) to be robust around obstacles.
            mobility = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if ok(ax, ay):
                    mobility += 1
            secondary = -mobility
        # Deterministic ordering for ties
        key = (-primary if is_evader else primary, secondary, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]