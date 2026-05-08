def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    turns = int(observation.get("turns_remaining", 0) or 0)
    parity = (sx + sy + turns) & 1

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_cell(rx, ry):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # prefer being closer than opponent
        if ((rx + ry) & 1) != parity:
            adv -= 0.2
        # small tie-break: prefer nearer overall and slight pressure toward opponent side
        adv -= 0.03 * sd
        adv += 0.02 * (ry - (h - 1 - oy))  # deterministic mild bias
        return adv

    best = None
    best_sc = -10**9
    best_sd = 10**9
    for rx, ry in resources:
        sc = score_cell(rx, ry)
        sd = man(sx, sy, rx, ry)
        if sc > best_sc or (sc == best_sc and sd < best_sd) or (sc == best_sc and sd == best_sd and (rx, ry) < best):
            best_sc = sc
            best_sd = sd
            best = (rx, ry)

    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
        # fall back to axis move deterministically
        candidates = []
        if dx != 0:
            candidates.append((dx, 0))
        if dy != 0:
            candidates.append((0, dy))
        candidates.append((0, 0))
        for cdx, cdy in candidates:
            nnx, nny = sx + cdx, sy + cdy
            if 0 <= nnx < w and 0 <= nny < h and (nnx, nny) not in obstacles:
                return [int(cdx), int(cdy)]
        return [0, 0]

    return [int(dx), int(dy)]