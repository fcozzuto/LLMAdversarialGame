def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    candidates = []
    for x, y in resources:
        sd = md(sx, sy, x, y)
        od = md(ox, oy, x, y)
        # Prefer targets where we can reach as fast or faster; otherwise minimize opponent advantage.
        lead = od - sd
        # Tie-break deterministically by favoring central-ish and lower sd.
        center = abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2)
        candidates.append((-(sd <= od + 1), -lead, center, sd, x, y))
    _, _, _, _, tx, ty = sorted(candidates)[0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in moves:
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        # Step cost: go toward target; also avoid moving into a state that makes opponent relatively closer.
        step_to_target = self_d
        deny_effect = (opp_d - self_d)
        # Small deterministic tie-break: prefer moves that progress toward target in x, then y.
        prog = (0 if tx == nx else 1 if (tx - nx) > 0 else -1, 0 if ty == ny else 1 if (ty - ny) > 0 else -1)
        key = (step_to_target, -deny_effect, abs(prog[0]), abs(prog[1]), dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]