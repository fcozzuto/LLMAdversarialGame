def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evad" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_penalty(x, y):
        if not obs:
            return 0.0
        best_m = 99
        for bx, by in obs:
            m = abs(x - bx) + abs(y - by)
            if m < best_m:
                best_m = m
        if best_m == 0:
            return 10000.0
        return 5.0 / best_m

    # Targeting: pursuer -> corners near evader/opponent to cut off; evader -> opposite corner from pursuer.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        # Evade toward the corner farthest from pursuer.
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        # Pursuer aims for the corner closest to opponent, to tighten and potentially capture sooner.
        tx, ty = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best_move = [0, 0]
    best_score = -10**18

    # Deterministic tie-breaking via fixed delta order and strict ">" scoring.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d_to_opp = dist2(nx, ny, ox, oy)
        d_to_corner = dist2(nx, ny, tx, ty)
        d_opp_to_corner = dist2(ox, oy, tx, ty)

        # Additional blocking term: prefer moves that increase opponent's distance-from-corner (evader)
        # or decrease it (pursuer), while also moving toward/away from target.
        if is_evader:
            score = (d_to_opp) - 0.6 * d_to_corner + 0.15 * (d_opp_to_corner) - obst_penalty(nx, ny)
        else:
            score = (-d_to_opp) + 0.3 * (-d_to_corner) + 0.15 * (-d_opp_to_corner) - obst_penalty(nx, ny)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move