def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_m(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # If we're standing on any visible resource, just avoid obstacles (collection should happen automatically).
    if (sx, sy) in set(resources):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        # Choose the best resource from the resulting position, but evaluate the move by "race advantage".
        best_gain_for_move = None
        for rx, ry in resources:
            self_d = dist_m(nx, ny, rx, ry)
            opp_d = dist_m(ox, oy, rx, ry)
            gain = opp_d - self_d  # positive means we are closer (faster race)
            # Prefer stronger advantage; if tied, prefer smaller self distance.
            tup = (gain, -self_d)
            if best_gain_for_move is None or tup > best_gain_for_move:
                best_gain_for_move = tup
        # Prefer moves that maximize the best available advantage; if tied, prefer smaller distance to that resource proxy.
        if best is None or best_gain_for_move > best:
            best = best_gain_for_move
            best_move = [dx, dy]

    return best_move