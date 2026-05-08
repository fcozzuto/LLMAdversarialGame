def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    # Default to pursuer if role is unclear
    is_evader = ("evad" in self_role) or ("runner" in self_role)
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_score = None
    best = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = abs(nx - ox) + abs(ny - oy)
        center_dist = abs(nx - cx) + abs(ny - cy)
        edge_pen = min(nx, w - 1 - nx, ny, h - 1 - ny)  # prefer staying away from edges for pursuer

        # When pursuer: minimize distance; tie-break toward center and toward lines that reduce escape
        if not is_evader:
            score = (-d, -abs((nx - ox) - (ny - oy)), edge_pen, -center_dist)
        else:
            # When evader: maximize distance; tie-break toward corners and away from center
            corner_dist = max(abs(nx - 0) + abs(ny - 0),
                              abs(nx - (w - 1)) + abs(ny - 0),
                              abs(nx - 0) + abs(ny - (h - 1)),
                              abs(nx - (w - 1)) + abs(ny - (h - 1)))
            score = (d, corner_dist, -center_dist)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]