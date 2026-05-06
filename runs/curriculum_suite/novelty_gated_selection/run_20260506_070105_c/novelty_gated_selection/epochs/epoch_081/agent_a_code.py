def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            score = man(nx, ny, cx, cy) - 0.25 * man(nx, ny, ox, oy)
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Opportunistic: pick a resource where we are relatively closer than opponent.
    bestT = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can likely reach first; when few resources remain, be more aggressive.
        rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
        urgency = 1.0 if rem > 4 else 1.4
        cand = (urgency * (od - myd), -myd, rx, ry)
        if bestT is None or cand > bestT[0]:
            bestT = (cand, (rx, ry))
    tx, ty = bestT[1]

    # Step towards target, but discourage moving into tighter opponent control.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_to = man(nx, ny, tx, ty)
        opp_to = man(nx, ny, ox, oy)
        # Also lightly prefer progressing in target direction.
        progress = abs(tx - nx) + abs(ty - ny)
        score = my_to + 0.15 * progress - 0.08 * opp_to
        key = (score, my_to, -opp_to, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]