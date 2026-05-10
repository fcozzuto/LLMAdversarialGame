def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    remaining = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    tight = 1 if remaining <= 6 else 0

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        margin = opp_d - my_d  # positive: we can arrive no later
        # Prefer: winning arrival; then closer path (smaller my_d);
        # small stability: prefer larger coords; plus mild "finish soon" pressure.
        finish_bonus = (h - 1 - ry) if tight else 0
        key = (
            margin,
            -my_d,
            finish_bonus,
            rx, ry
        )
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best

    # Greedy step toward target, but avoid stepping into known obstacles if possible.
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                cand.append((cheb(sx, sy, tx, ty), 0, 0))
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((cheb(nx, ny, tx, ty), dx, dy))
    cand.sort(key=lambda t: (t[0], -t[1], -t[2], t[1] if t[1] >= 0 else -t[1], t[2] if t[2] >= 0 else -t[2]))
    return [int(cand[0][1]), int(cand[0][2])]