def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = c - a
        dy = d - b
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_for(nx, ny):
        # Prefer getting/maintaining a lead on the most contested resource.
        best = -10**18
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            lead = opd - myd  # positive means we are closer now
            # Tie-break toward nearer resource, then lexicographically.
            score = lead * 1000 - myd - opd + (-(rx * 10 + ry) * 0)
            if score > best:
                best = score
                best_cell = (rx, ry)
        return best

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        candidates.append((best_for(nx, ny), dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]