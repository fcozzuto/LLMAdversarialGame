def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            moves.append((dx, dy, nx, ny))

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy, nx, ny in moves:
        worst = -1
        # opponent maximizes distance to us on its turn (worst-case)
        for odx, ody in deltas:
            nox, noy = ox + odx, oy + ody
            if not valid(nox, noy):
                continue
            d = manh(nx, ny, nox, noy)
            if d > worst:
                worst = d
        # if opponent has no legal moves (rare), treat as staying
        if worst < 0:
            worst = manh(nx, ny, ox, oy)
        curdist = manh(nx, ny, ox, oy)
        score = (worst, curdist, -abs(dx) - abs(dy), dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]