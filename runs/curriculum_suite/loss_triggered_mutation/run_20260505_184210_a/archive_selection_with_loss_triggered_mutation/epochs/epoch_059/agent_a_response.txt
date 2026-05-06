def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # "Interceptor" focus: pick a target where we arrive no later than opponent, maximizing our advantage.
    best = None
    for cell in resources:
        sd = dist((sx, sy), cell)
        od = dist((ox, oy), cell)
        adv = od - sd  # positive means we are closer
        # tie-break deterministically: higher advantage, then smaller our distance, then lexicographically
        key = (-adv, sd, cell[0], cell[1])  # reversed for deterministic min()
        if best is None or key < best[0]:
            best = (key, cell, sd, od, adv)
    cell = best[1]
    tx, ty = cell

    # Move one step toward target, trying to avoid obstacles; deterministically choose best among legal deltas.
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    chosen = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer reducing distance to target; if equal, keep also reducing opponent's likely access by maintaining advantage
        nd = dist((nx, ny), (tx, ty))
        oppd = dist((ox, oy), (tx, ty))
        step_adv = oppd - nd
        key = (nd, -step_adv, abs(ox - nx) + abs(oy - ny), dx, dy)
        if chosen is None or key < chosen[0]:
            chosen = (key, [dx, dy])
    if chosen is None:
        return [0, 0]
    return chosen[1]