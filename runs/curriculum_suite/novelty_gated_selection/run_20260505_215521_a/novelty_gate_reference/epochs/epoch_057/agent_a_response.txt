def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        best_val = -10**18
        for rx, ry in resources:
            us = dist((sx, sy), (rx, ry))
            op = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach sooner, discourage ones opponent is much closer to.
            val = (op - us) * 2 - us * 0.35 - op * 0.05
            # Small tie-break towards center to stabilize.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val -= (abs(rx - cx) + abs(ry - cy)) * 0.01
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose best next step w.r.t. the chosen target, with obstacle-aware fallback and competition penalty.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        us = dist((nx, ny), (tx, ty))
        op = dist((ox, oy), (tx, ty))
        score = (op - us) * 2 - us * 0.35 - op * 0.05
        # If resources exist, add mild preference to move closer to some resource that opponent can't take easily.
        if resources:
            # Deterministic quick scan: evaluate only first few resources.
            limit = min(6, len(resources))
            add = 0
            for i in range(limit):
                rx, ry = resources[i]
                if (rx, ry) in obstacles:
                    continue
                us2 = dist((nx, ny), (rx, ry))
                op2 = dist((ox, oy), (rx, ry))
                add += max(0, op2 - us2) * 0.15 - us2 * 0.01
            score += add
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]