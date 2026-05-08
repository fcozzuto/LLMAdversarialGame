def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = [tuple(map(int, xy)) for xy in (observation.get("unclaimed_cells", []) or []) if len(xy) >= 2]
    opp_terr = [tuple(map(int, xy)) for xy in (observation.get("opponent_territory", []) or []) if len(xy) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    candidates = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18

    target_points = unclaimed if unclaimed else (opp_terr if opp_terr else [(ox, oy)])

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Encourage moving closer to resources/unclaimed; if none, push toward opponent/contested.
        md = 10**9
        for tx, ty in target_points:
            d = man(nx, ny, tx, ty)
            if d < md:
                md = d
        score = -md

        # Slightly avoid moving away from opponent when no unclaimed exists.
        if not unclaimed and opp_terr:
            score += -man(nx, ny, ox, oy) * 0.1

        # Deterministic tie-break: prefer (0,0) last, and lower dx then dy.
        tie = (0 if (dx, dy) != (0, 0) else -0.01) + (-(dx + 1)) * 1e-6 + (-(dy + 1)) * 1e-12
        score += tie

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best