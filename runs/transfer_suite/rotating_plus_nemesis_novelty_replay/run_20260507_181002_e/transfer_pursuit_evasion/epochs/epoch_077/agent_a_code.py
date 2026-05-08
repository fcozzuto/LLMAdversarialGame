def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    self_is_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("seeker" in sr) or ("hunter" in sr) or ("tagger" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def greedy_move(px, py, tx, ty, want_max):
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not legal(nx, ny):
                continue
            val = d2(nx, ny, tx, ty)
            if best_val is None or (want_max and val > best_val) or ((not want_max) and val < best_val):
                best_val = val
                best = (dx, dy)
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not legal(nsx, nsy):
            continue
        if self_is_pursuer:
            nox, noy = greedy_move(ox, oy, nsx, nsy, want_max=True)
            res_score = d2(nsx + nox * 0, nsy + noy * 0, (ox + nox), (oy + noy))
        else:
            nox, noy = greedy_move(ox, oy, nsx, nsy, want_max=False)
            res_score = d2(nsx, nsy, (ox + nox), (oy + noy))
        # Pursuer chooses smaller distance; evader chooses larger distance
        want_max = not self_is_pursuer
        if best_score is None or (want_max and res_score > best_score) or ((not want_max) and res_score < best_score) or (res_score == best_score and (dx, dy) < best_move):
            best_score = res_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]