def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def sqdist(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Pressure heuristic: reduce distance; prefer moves that also "cut off" by limiting opponent escape.
    # Wall-run nerf: prefer staying aligned with opponent's direction (diagonal/axial components).
    best = None
    cur_d = sqdist(sx, sy, ox, oy)

    for dx, dy, nx, ny in candidates:
        d = sqdist(nx, ny, ox, oy)

        # "Escape-limiting": count how many moves from opponent would increase its distance from our new position.
        opp_moves = []
        for adx, ady in moves:
            ax, ay = ox + adx, oy + ady
            if inside(ax, ay):
                opp_moves.append((ax, ay))
        if opp_moves:
            inc = 0
            for ax, ay in opp_moves:
                if sqdist(ax, ay, nx, ny) >= sqdist(ox, oy, nx, ny):
                    inc += 1
            escape_score = inc
        else:
            escape_score = 0

        align = abs((nx - ox)) + abs((ny - oy))  # closer means less
        move_delta = cur_d - d  # positive is good

        # Score: lexicographic on best pressure; deterministic tie-breaks.
        score = (
            d,                 # primary: get close
            escape_score,      # secondary: reduce opponent escape options
            align,             # secondary: keep pressure on approach path
            -move_delta,       # prefer bigger improvement this turn
            (dx != 0) + (dy != 0),  # slight preference for diagonal when equal
            dx, dy
        )
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]