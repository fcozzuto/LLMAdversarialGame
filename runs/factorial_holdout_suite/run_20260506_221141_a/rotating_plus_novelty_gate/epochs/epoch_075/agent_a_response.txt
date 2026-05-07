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

    tr = int(observation.get("turn_index", 0) or 0)

    # Heuristic: maximize "reach advantage" over opponent; if similar, prefer resources that opponent is less likely to sweep into next.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = mhd(sx, sy, rx, ry)
        od = mhd(ox, oy, rx, ry)
        adv = od - sd  # positive means we can arrive sooner
        # Opponent sweep_rows tends to value low travel in y and then moving along x; prefer resources with less opponent vertical progress.
        opp_y_progress = abs(oy - ry)
        # Deterministic turn modulation: alternate between pushing advantage and denying likely next sweep.
        mode = 1 if (tr % 2 == 0) else -1
        key = (mode * adv, -opp_y_progress, -sd, (rx + 3 * ry) % 7)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose a legal move that reduces distance to target; if blocked, try alternatives.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            dist = mhd(nx, ny, tx, ty)
            # Small deterministic tie-breaker to avoid dithering near equal targets.
            tieb = (nx * 13 + ny * 7 + tx * 3 + ty) % 11
            candidates.append((dist, tieb, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]