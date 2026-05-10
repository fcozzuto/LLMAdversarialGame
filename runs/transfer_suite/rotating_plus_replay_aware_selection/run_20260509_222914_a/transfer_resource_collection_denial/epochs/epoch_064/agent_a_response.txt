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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Find best target under a "resource denial" assumption:
        # opponent effectively reduces their distance by ~1 on their next move.
        best_target_key = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry) - 1
            if od < 0:
                od = 0
            # Prefer being able to arrive sooner (or equal but with smaller slack).
            win = 1 if sd <= od else 0
            slack = od - sd  # larger is better
            # Tie-break: closer overall to reduce future exposure.
            self_closer = -sd
            # Also slightly prefer moving toward resources that are closer to centerless (deterministic stable)
            # by adding a small deterministic hash from coordinates.
            hbonus = -((rx * 13 + ry * 7) % 10) / 100.0
            key = (win, slack, self_closer, hbonus)
            if best_target_key is None or key > best_target_key:
                best_target_key = key

        if best_target_key is None:
            continue

        # Additionally discourage stepping adjacent to opponent if it doesn't improve arrival.
        opp_adj = cheb(nx, ny, ox, oy)
        risk = 1 if opp_adj == 0 else (1 if opp_adj == 1 else 0)

        move_key = (best_target_key[0], best_target_key[1], best_target_key[2], -risk, best_target_key[3], dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best = [dx, dy]

    return [int(best[0]), int(best[1])]