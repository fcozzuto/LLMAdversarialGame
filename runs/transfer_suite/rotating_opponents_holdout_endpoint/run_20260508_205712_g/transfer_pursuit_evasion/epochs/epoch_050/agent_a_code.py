def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "pursuer") or "pursuer").lower()
    pursue = role != "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    wantx = ox - sx
    wanty = oy - sy
    step_pref = (1 if wantx > 0 else (-1 if wantx < 0 else 0), 1 if wanty > 0 else (-1 if wanty < 0 else 0))

    best = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)

        # Primary: distance to opponent (min for pursuer, max for evader)
        primary = -d if pursue else d

        # Secondary: move along intended direction (deterministic tie-break)
        align = -(abs(dx - step_pref[0]) + abs(dy - step_pref[1]))
        # Tertiary: prefer moving (or staying) deterministically to avoid oscillation
        still_pen = 1 if (dx == 0 and dy == 0) else 0

        val = primary * 100.0 + align * 1.0 - still_pen * 0.01
        if bestv is None or val > bestv:
            bestv = val
            best = (dx, dy)

    if bestv is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]