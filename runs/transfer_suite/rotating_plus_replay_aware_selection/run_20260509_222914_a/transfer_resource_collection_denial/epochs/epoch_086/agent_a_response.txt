def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
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

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonals allowed)

    best_move = [0, 0]
    best_val = None
    best_sec = None
    best_third = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # For this prospective position, pick the most favorable resource.
        # Primary: maximize (opp_dist - self_dist). Secondary: minimize self_dist. Tertiary: favor smaller opp_dist.
        best_tup = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            tup = (od - sd, -sd, -od)  # sort descending by first, then descending by -sd, then descending by -od
            if best_tup is None or tup > best_tup:
                best_tup = tup

        val, negsd, negod = best_tup
        sec = -negsd
        third = -negod

        if best_val is None or val > best_val or (val == best_val and (sec < best_sec or (sec == best_sec and third < best_third))):
            best_val, best_sec, best_third = val, sec, third
            best_move = [dx, dy]

    return best_move