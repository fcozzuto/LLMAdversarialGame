def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def blocked(x, y):
        return (x, y) in obstacles or not (0 <= x < w and 0 <= y < h)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def open_neighbors(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    def score(nx, ny):
        md = abs(nx - ox) + abs(ny - oy)
        trap = 8 - open_neighbors(nx, ny)  # higher => more blocked around
        # also avoid moving into an obstacle-adjacent "net" around opponent
        opp_trap = 0
        for dx, dy in moves:
            tx, ty = nx + dx, ny + dy
            if 0 <= tx < w and 0 <= ty < h:
                if (tx, ty) in obstacles:
                    opp_trap += 1
        if is_evader:
            # maximize distance, avoid traps
            return (md * 4) - (trap * 3) - opp_trap
        else:
            # minimize distance, avoid traps
            return (-md * 4) - (trap * 2) - opp_trap

    best = None
    best_sc = None
    # deterministic tie-break: fixed move ordering, then lexicographic by delta
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        sc = score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best