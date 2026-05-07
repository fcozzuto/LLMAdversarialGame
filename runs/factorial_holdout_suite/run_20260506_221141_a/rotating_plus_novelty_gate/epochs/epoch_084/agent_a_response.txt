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

    best = None
    best_score = -10**18
    for rx, ry in resources:
        sd = mhd(sx, sy, rx, ry)
        od = mhd(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        # Strongly prefer resources where we arrive no later than opponent; then maximize arrival advantage.
        arrive_adv = od - sd
        # Small bias toward closer targets to reduce stalling and improve endgame certainty.
        closeness = -sd
        # Deterministic tie-break by coordinates.
        tb = -(rx * 31 + ry)
        score = arrive_adv * 1000 + closeness * 10 + tb
        if sd <= od + 1:
            score += 500
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    best_step = (0, 0)
    best_d = 10**18
    # Try all moves including diagonals, then choose deterministic best that doesn't step into obstacles.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                d = mhd(nx, ny, tx, ty)
                # Prefer decreasing distance to target; tie-break deterministically by dx,dy.
                if d < best_d or (d == best_d and (dx, dy) < best_step):
                    best_d = d
                    best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]