def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or self_role == "evader"
    opp_is_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or opp_role == "evader"

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def valid_moves_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                out.append((dx, dy, nx, ny))
        return out if out else [(0, 0, x, y)]

    def pick_move(x, y, tx, ty, evader, prefer_center=True):
        best = None
        bestt = None
        for dx, dy, nx, ny in valid_moves_from(x, y):
            d = man(nx, ny, tx, ty)
            # For evader: prefer larger distance; for pursuer: prefer smaller distance.
            score = d if evader else -d
            if prefer_center:
                # tie-break: move slightly toward center for determinism/unsticking
                score2 = -((nx - cx) ** 2 + (ny - cy) ** 2)
            else:
                score2 = 0
            key = (score, score2)
            if best is None or key > bestt:
                bestt = key
                best = [dx, dy]
        return best

    # 2-ply deterministic lookahead: our move, then opponent best response
    best_key = None
    best_move = [0, 0]
    for dx, dy, nx, ny in valid_moves_from(sx, sy):
        # If we are pursuer, we want opponent's distance to be small after their response.
        # If we are evader, we want it large after their response.
        opp_move = pick_move(ox, oy, nx, ny, opp_is_evader, prefer_center=False)
        odx, ody = opp_move
        nox, noy = ox + odx, oy + ody
        # Clamp via validity assumption; engine otherwise keeps in place
        if not inb(nox, noy) or (nox, noy) in obs_set:
            nox, noy = ox, oy
        d_after = man(nx, ny, nox, noy)

        # Add slight bias to improve robustness: if pursuer, also prefer reducing distance now.
        now_d = man(nx, ny, ox, oy)
        if self_is_evader:
            key = (d_after, d_after - now_d)
        else:
            key = (-d_after, -(now_d))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move