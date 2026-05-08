def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda q: abs(q[0] - sx) + abs(q[1] - sy))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    tox = abs(ox - sx) + abs(oy - sy)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = abs(tx - nx) + abs(ty - ny)
        d_to_opp = abs(ox - nx) + abs(oy - ny)
        prefer = 0
        # Prefer moves that approach target and don't let opponent get much closer
        v = -d_to_t + 0.2 * (d_to_opp - tox)
        if (nx, ny) == (sx, sy):
            v -= 0.3
        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]