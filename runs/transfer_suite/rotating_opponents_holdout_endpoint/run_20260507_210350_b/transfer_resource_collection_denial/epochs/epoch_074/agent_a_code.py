def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_t = None
    best_adv = -10**9
    for x, y in resources:
        ds = md(sx, sy, x, y)
        do = md(ox, oy, x, y)
        adv = (do - ds) * 10 - ds * 0.2  # maximize advantage, then prefer closer
        if adv > best_adv:
            best_adv = adv
            best_t = (x, y)

    # If no clear advantage, fall back to nearest resource (often helps vs shadow-like opponent).
    if best_adv < 0:
        best_t = min(resources, key=lambda t: md(sx, sy, t[0], t[1]))

    tx, ty = best_t

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            if nx == sx and ny == sy:
                # Staying still is allowed; still evaluate like other moves.
                pass
            step_cost = md(nx, ny, tx, ty) + 0.12 * md(nx, ny, ox, oy)
            # Small bias to progress diagonally when both are helpful.
            if dx != 0 and dy != 0:
                step_cost -= 0.01
            candidates.append((step_cost, dx, dy))

    candidates.sort()
    return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]