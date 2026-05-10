def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        beat = 1 if my_d <= opp_d else 0
        # Prefer resources I can beat; then maximize (opp_d - my_d).
        # Tie-break deterministically toward smaller travel, then "higher" (rx+ry).
        score = (beat, opp_d - my_d, -my_d, -(rx + ry), -rx)
        if best is None or score > best[0]:
            best = (score, (rx, ry))

    tx, ty = best[1]
    direct = (0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1))

    deltas = [direct, (direct[0], 0), (0, direct[1]), (direct[0], -direct[1]), (0 if direct[0] == 0 else -direct[0], 0),
              (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1), (0, 0)]
    seen = set()
    ordered = []
    for dx, dy in deltas:
        if (dx, dy) in seen:
            continue
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            ordered.append((dx, dy))
            seen.add((dx, dy))

    best_move = (0, 0)
    best_dist = None
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        if best_dist is None or d < best_dist:
            best_dist = d
            best_move = (dx, dy)

    if best_dist is None:
        dx, dy = direct
        return [dx, dy]
    return [int(best_move[0]), int(best_move[1])]