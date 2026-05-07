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

    # Contest opponent's likely "row sweep": heavily prefer resources on opponent's current y.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        self_d = mhd(sx, sy, rx, ry)
        opp_d = mhd(ox, oy, rx, ry)

        # If on opponent's current row, assume higher contest likelihood; also bias toward reducing our row gap.
        row_bias = 0
        if ry == oy:
            row_bias = 120
        else:
            # favor moving closer to that sweep row even if not currently on it
            row_gap = ry - oy
            if row_gap < 0: row_gap = -row_gap
            row_bias = -8 * row_gap

        # Primary: create advantage over opponent on the resource.
        # Secondary: prefer closer targets to reduce commitment errors.
        val = (opp_d - self_d) + row_bias - 0.15 * self_d

        # Small tie-break: closer by max coordinate alignment with opponent direction.
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    dx = tx - sx
    if dx > 0: dx = 1
    elif dx < 0: dx = -1
    dy = ty - sy
    if dy > 0: dy = 1
    elif dy < 0: dy = -1

    # Avoid stepping into known obstacles if possible by adjusting one axis.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in blocked:
        # Try axis moves deterministically
        if (sx + dx, sy) not in blocked:
            return [dx, 0]
        if (sx, sy + dy) not in blocked:
            return [0, dy]
        return [0, 0]

    return [dx, dy]