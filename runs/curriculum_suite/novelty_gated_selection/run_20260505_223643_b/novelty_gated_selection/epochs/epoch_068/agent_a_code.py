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
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, 1), (-1, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def cand_score(nx, ny):
        best = -10**18
        for rx, ry in resources:
            myd = dist2(nx, ny, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            # Prefer being closer than opponent; then prefer smaller my distance.
            val = (opd - myd) * 1000 - myd
            # Slightly encourage moving toward resources already near.
            if myd == 0:
                val += 10**9
            best = val if val > best else best
        return best

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = cand_score(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            # Deterministic tie-break: lexicographic by (dx,dy), then prefer staying/short moves.
            if [dx, dy] < best_move:
                best_move = [dx, dy]
    return best_move