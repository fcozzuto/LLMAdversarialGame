def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = moves

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def adj_block_cnt(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                c += 1
        return c

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny)
        block = adj_block_cnt(nx, ny)
        score = (d - 0.08 * block) if am_evader else (-d - 0.08 * block)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                best = (dx, dy)
                break
    return [best[0], best[1]] if best is not None else [0, 0]