def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_val = None  # tuple for lexicographic comparison

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Aim for a resource we can reach earlier than the opponent; otherwise go for closest.
        cur_best_for_move = None
        for rx, ry in resources:
            self_d = manhattan(nx, ny, rx, ry)
            opp_d = manhattan(ox, oy, rx, ry)

            # Primary: maximize "winning margin" (opp_d - self_d)
            # Secondary: minimize self_d (finish earlier)
            # Tertiary: minimize resource distance to our next position (stable)
            val = (opp_d - self_d, -self_d, self_d)
            if cur_best_for_move is None or val > cur_best_for_move:
                cur_best_for_move = val

        if cur_best_for_move is None:
            continue

        # Compare moves: maximize winning margin; if tied, prefer smaller self_d; if still tied, prefer staying still
        overall = (cur_best_for_move[0], -cur_best_for_move[1], cur_best_for_move[2], -int(dx == 0 and dy == 0))
        if best_val is None or overall > best_val:
            best_val = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]