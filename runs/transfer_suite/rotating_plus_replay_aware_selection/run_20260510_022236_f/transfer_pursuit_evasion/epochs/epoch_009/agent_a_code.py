def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) and ("purs" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    corner = corners[phase]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def neighbors_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        ncnt = neighbors_count(nx, ny)

        if is_evader:
            cx, cy = corner
            corner_bias2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            score = dist2 + 0.35 * corner_bias2 + 0.08 * ncnt
        else:
            score = -dist2 + 0.25 * ncnt

        if dist2 == 0 and not is_evader:
            score += 1000000
        elif dist2 == 0 and is_evader:
            score -= 1000000

        if best_score is None or (score > best_score):
            best_score = score
            best = [dx, dy]

    return best