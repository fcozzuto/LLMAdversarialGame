def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can reach earlier (deny), but keep pressure even if behind.
        v = (od - sd) * 3 - sd * 0.25 + (od == 0) * 0.0
        tieb = (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)) * -0.01
        key = (v + tieb, -od, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            # Move value: closer to target; small bias to also move away from opponent if tie.
            dcur = man(sx, sy, tx, ty)
            dnxt = man(nx, ny, tx, ty)
            oppdcur = man(sx, sy, ox, oy)
            oppdnxt = man(nx, ny, ox, oy)
            val = (dcur - dnxt) * 10 + (oppdnxt - oppdcur) * 0.15
            # Deterministic tie-break
            moves.append(((val, -dnxt, dx, dy), dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda z: z[0], reverse=True)
    return [moves[0][1], moves[0][2]]