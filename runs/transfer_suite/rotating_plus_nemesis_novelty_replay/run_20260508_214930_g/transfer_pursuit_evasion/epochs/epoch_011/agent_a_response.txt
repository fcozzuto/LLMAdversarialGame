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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def next_pos(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            return x, y
        return nx, ny
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If we can capture by overlapping (capture_radius=0), do it.
    for dx, dy in actions:
        nsx, nsy = next_pos(sx, sy, dx, dy)
        if nsx == ox and nsy == oy:
            return [dx, dy]

    best_move = [0, 0]
    best_val = None

    for dx, dy in actions:
        nsx, nsy = next_pos(sx, sy, dx, dy)

        # Predict opponent: choose its move that maximizes distance to our next position.
        max_d = -1
        pred = (ox, oy)
        for odx, ody in actions:
            nox, noy = next_pos(ox, oy, odx, ody)
            d = dist2(nox, noy, nsx, nsy)
            if d > max_d:
                max_d = d
                pred = (nox, noy)
        nox, noy = pred

        # Choose our move that minimizes the predicted next distance (intercept).
        val = dist2(nsx, nsy, nox, noy)

        # Tie-breaks: prefer moves that also progress toward opponent (smaller current distance).
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            cur_best = dist2(sx, sy, ox, oy)
            cur_new = dist2(next_pos(sx, sy, dx, dy)[0], next_pos(sx, sy, dx, dy)[1], ox, oy)
            if cur_new < cur_best:
                best_move = [dx, dy]

    return best_move