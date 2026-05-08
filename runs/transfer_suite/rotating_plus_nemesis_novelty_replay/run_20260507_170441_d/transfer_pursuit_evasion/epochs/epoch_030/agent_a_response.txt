def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ddx = nx - ox
        ddy = ny - oy
        score = ddx * ddx + ddy * ddy  # maximize distance (evade)
        # tie-breakers: prefer moves that also avoid reducing distance next step
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            # prefer staying near center to reduce corner-trap likelihood
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            cur = (sx, sy)
            cand = (nx, ny)
            best_cand = (sx + best[0], sy + best[1])
            cur_d = abs(cur[0] - cx) + abs(cur[1] - cy)
            cand_d = abs(cand[0] - cx) + abs(cand[1] - cy)
            best_d = abs(best_cand[0] - cx) + abs(best_cand[1] - cy)
            # only adjust on equal distance ties: move that increases center proximity
            if (cand_d < best_d) or (cand_d <= cur_d and best_d > cur_d):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]