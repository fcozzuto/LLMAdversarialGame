def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def mhd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    tr = int(observation.get("turns_remaining", 0) or 0)
    best = None
    best_val = -10**18

    # Score resources by (1) how much sooner we can reach than opponent, (2) opponent row pressure, (3) safety for timing.
    for rx, ry in resources:
        sd = mhd(sx, sy, rx, ry)
        od = mhd(ox, oy, rx, ry)
        # Bonus if we can arrive strictly before/while opponent likely contesting.
        advantage = od - sd  # positive means we are earlier
        if sd == 0:
            advantage = 6  # already on resource
        row_press = 5 if ry == oy else 0
        horizon = 2 if sd <= tr else -3
        # Mild center/diagonal smoothness: prefer staying away from extreme edges late is not reliable; instead prefer not chasing too far.
        far_pen = 0.25 * sd
        val = (3.5 * advantage) + row_press + horizon - far_pen
        # If distances tie, prefer resource that moves us toward opponent's side (y higher), increasing race pressure.
        if advantage == 0:
            val += 0.8 if (ry > sy) else -0.3
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    dx = 0
    if rx > sx: dx = 1
    elif rx < sx: dx = -1
    dy = 0
    if ry > sy: dy = 1
    elif ry < sy: dy = -1

    # If moving toward target would be blocked, take a deterministic detour by dropping the step on one axis.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in blocked:
        # Try axis-aligned alternatives deterministically: keep the larger progress axis first.
        a1 = (sx + dx, sy)
        a2 = (sx, sy + dy)
        if a1[0] == sx and a1[1] == sy:
            return [0, 0]
        if 0 <= a1[0] < w and 0 <= a1[1] < h and a1 not in blocked:
            return [dx, 0]
        if 0 <= a2[0] < w and 0 <= a2[1] < h and a2 not in blocked:
            return [0, dy]
        return [0, 0]
    return [dx, dy]