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

    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        self_d = mhd(sx, sy, rx, ry)
        opp_d = mhd(ox, oy, rx, ry)
        v = 0
        # Strongly prioritize the row the opponent is currently sweeping.
        if ry == oy:
            v += 800
        # Also prefer rows close to opponent.
        v += 120 - 20 * mhd(ox, oy, ox, ry)
        # Prefer resources we can beat them to.
        if self_d < opp_d:
            v += 250 - 10 * self_d
        else:
            v += -80 - 10 * (self_d - opp_d)
        # Mild preference for closeness.
        v += 30 - 2 * self_d
        # If tied, prefer the one with lexicographically smaller coordinate (deterministic).
        if v > best_val or (v == best_val and (best_r is None or (rx, ry) < best_r)):
            best_val = v
            best_r = (rx, ry)

    tx, ty = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_mval = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        # Prefer immediate progress to target and reduce chance of being slower than opponent.
        self_next = mhd(nx, ny, tx, ty)
        opp_d = mhd(ox, oy, tx, ty)
        v = -self_next
        if self_next <= opp_d:
            v += 60
        if (nx, ny) == (tx, ty):
            v += 2000
        # Discourage moving away from opponent's sweep row when already aligned.
        if ty == oy:
            v += -abs(ny - oy) * 2
        if v > best_mval or (v == best_mval and (dx, dy) < best_m):
            best_mval = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]