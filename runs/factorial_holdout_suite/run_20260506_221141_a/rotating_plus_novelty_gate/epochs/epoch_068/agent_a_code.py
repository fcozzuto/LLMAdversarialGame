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

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_val = -10**18
    opp_row = oy
    my_row = sy
    for rx, ry in resources:
        my_d = manh(sx, sy, rx, ry)
        opp_d = manh(ox, oy, rx, ry)
        if my_d == 0:
            return [0, 0]
        # If we can arrive first, go for value; otherwise, still contest if opponent is much closer.
        can_first = my_d <= opp_d
        row_contest = 18 if ry == opp_row else 0
        corridor = 8 if (rx == sx) or (ry == sy) else 0
        base = 1000 - 12 * my_d + row_contest + corridor
        if can_first:
            val = base + (opp_d - my_d) * 60
        else:
            val = 260 - 8 * opp_d + (opp_d - my_d) * 30 + (ry == my_row) * 10
        # Mild preference to move generally toward opponent's side without full search
        val += (rx > sx) * 2 + (ry < h - 1) * 1
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try direct step; if blocked, try alternative steps in a deterministic priority toward the target.
    candidates = []
    candidates.append((dx, dy))
    # Prioritize keeping distance reducing; try axis moves if diagonal invalid.
    candidates.append((dx, 0))
    candidates.append((0, dy))
    candidates.append((-dx, dy))
    candidates.append((dx, -dy))
    candidates.append((0, 0))
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [int(cdx), int(cdy)]
    return [0, 0]