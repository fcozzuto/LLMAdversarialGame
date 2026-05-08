def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    opp_is_evader = ("evader" in orr) or ("runner" in orr)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_opp_move(ax, ay, tx, ty, opp_ev):
        best_score = None
        best = (0, 0)
        # deterministic tie-break: lexicographic by (dx,dy) after score
        for dx, dy in moves:
            nx, ny = tx + dx, ty + dy
            if not free(nx, ny):
                continue
            d = abs(nx - ax) + abs(ny - ay)
            score = d if opp_ev else -d
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        return best

    best_move = (0, 0)
    best_val = None

    if not self_is_evader:
        # pursuer: predict opponent response and move to minimize distance
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            opp_dx, opp_dy = best_opp_move(nx, ny, ox, oy, opp_is_evader)
            nox, noy = ox + opp_dx, oy + opp_dy
            d = abs(nox - nx) + abs(noy - ny)
            val = -d  # maximize negative distance
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
    else:
        # evader: predict opponent response and move to maximize distance
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            opp_dx, opp_dy = best_opp_move(nx, ny, ox, oy, opp_is_evader)
            nox, noy = ox + opp_dx, oy + opp_dy
            d = abs(nox - nx) + abs(noy - ny)
            val = d
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]