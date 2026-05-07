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

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Choose a target: prioritize resources where we can arrive before opponent.
    best = None
    for rx, ry in resources:
        sd = man(rx, ry, sx, sy)
        od = man(rx, ry, ox, oy)
        # If opponent is closer or equal, heavily penalize.
        if od <= sd:
            score = -1000 + (od - sd)  # far worse when equal/closer
        else:
            # Prefer earlier arrival, and slightly closer to us for feasibility.
            score = (od - sd) * 20 - sd
        # Small deterministic tiebreak
        score -= (rx + 3 * ry) * 0.001
        cand = (score, rx, ry)
        if best is None or cand > best:
            best = cand

    _, tx, ty = best

    # Step greedily toward chosen target; evaluate all 9 moves with a deterministic tiebreak.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, man(nx, ny, tx, ty), man(nx, ny, ox, oy)))
    # Deterministic ordering: closer to target first, then farther from opponent, then lexicographic.
    moves.sort(key=lambda m: (m[2], -m[3], m[0], m[1]))
    return [int(moves[0][0]), int(moves[0][1])]