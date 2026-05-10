def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in sr) and not ("evad" in orr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def free_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    far_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: manh(c[0], c[1], ox, oy))
    target = far_corner if self_is_evader else near_corner

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_opp = manh(nx, ny, ox, oy)
        d_to_tgt = manh(nx, ny, target[0], target[1])
        fc = free_count(nx, ny)
        # Encourage corner strategy, avoid getting closer as evader; as pursuer, close distance and restrict.
        if self_is_evader:
            score = (d_to_opp * 3) + (d_to_tgt * 1) + (fc * 0.35) - (manh(nx, ny, ox + (ox - sx), oy + (oy - sy)) * 0.15)
        else:
            # slight bias to near_corner while pursuing directly
            score = (-d_to_opp * 3) + (-d_to_tgt * 0.8) + (fc * 0.15) + (0.05 if (nx, ny) == target else 0.0)

        # Deterministic tie-break: lexicographic on (dx,dy) with earlier preference in deltas
        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]