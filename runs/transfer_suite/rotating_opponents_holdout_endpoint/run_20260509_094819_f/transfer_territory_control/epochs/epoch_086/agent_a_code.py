def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    op = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            obs.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b, c, e):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - e
        if dy < 0: dy = -dy
        return dx + dy

    un = observation.get("unclaimed_cells") or []
    un2 = []
    for p in un:
        if not p or len(p) < 2: 
            continue
        x, y = int(p[0]), int(p[1])
        if inb(x, y) and (x, y) not in obs:
            un2.append((x, y))
    if un2:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        un2.sort(key=lambda t: (abs(t[0] - cx) + abs(t[1] - cy), d(sx, sy, t[0], t[1])))
        targets = un2[:24]
    else:
        # Fallback: follow a deterministic sweep toward the center while avoiding obstacles
        targets = [(w // 2, h // 2), (w // 2, 0), (0, h // 2), (w - 1, h // 2), (w // 2, h - 1)]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer legal-looking moves; if obstacle, still allow but heavily penalize
        if (nx, ny) in obs:
            base_penalty = 10**6
        else:
            base_penalty = 0

        # Greedy: minimize distance to an advantageous unclaimed target; slight bias away from opponent
        score = base_penalty
        for tx, ty in targets:
            ds = d(nx, ny, tx, ty)
            do = d(ox, oy, tx, ty)
            val = ds - 0.25 * do
            if score == base_penalty or val < score - base_penalty:
                score = base_penalty + val
        # Tie-break deterministically by move order preference
        if best is None or score < best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]