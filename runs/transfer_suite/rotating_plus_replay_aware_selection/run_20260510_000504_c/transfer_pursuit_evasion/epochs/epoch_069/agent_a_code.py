def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("purs" in opp_role)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_score = -10**18 if self_evader else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        # Prefer moving away if evader; toward if pursuer; add slight center bias deterministically.
        center_bias = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
        if self_evader:
            score = d * 1000 + center_bias
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score, best_move = score, (dx, dy)
        else:
            score = (-d) * 1000 + center_bias
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]