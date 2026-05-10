def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            try:
                obs.add((int(b[0]), int(b[1])))
            except:
                pass

    actions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    blocked = lambda x, y: (x, y) in obs

    def next_pos(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            return x, y
        return nx, ny

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = actions[4]
    best_score = None

    for dx, dy in actions:
        nsx, nsy = next_pos(sx, sy, dx, dy)
        if nsx == ox and nsy == oy:
            return [dx, dy]

        # Opponent evasion: choose move that maximizes distance to our next position.
        worst = -1
        # Deterministic tie-break: prefer earlier actions for maximizing.
        for odx, ody in actions:
            nox, noy = next_pos(ox, oy, odx, ody)
            d = dist2(nsx, nsy, nox, noy)
            if d > worst:
                worst = d
        score = -worst  # minimize worst-case distance squared

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]