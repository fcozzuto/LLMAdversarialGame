def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose a target we can beat the opponent on (self earlier than opponent), else closest.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        advantage = (od - sd)  # higher is better
        # Tie-break: smaller self distance and prefer resources "toward center" from our side.
        center_bias = abs((rx - (w - 1 - sx)) - (ry - (h - 1 - sy)))
        key = (advantage, -sd, -center_bias, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        candidates = [(0, 0, sx, sy)]

    bestm = None
    for dx, dy, nx, ny in candidates:
        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Prefer decreasing our distance to target; also try to keep opp farther (or block by moving toward target quickly).
        score = (-(self_d), (opp_d - man(nx, ny, tx, ty)) , -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        # If target coincides, head to it no matter what (distance will be 0).
        if bestm is None or score > bestm[0]:
            bestm = (score, (dx, dy))
    return [int(bestm[1][0]), int(bestm[1][1])]