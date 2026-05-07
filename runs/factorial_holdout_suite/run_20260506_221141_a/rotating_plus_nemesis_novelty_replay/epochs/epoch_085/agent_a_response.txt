def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    # Move evaluation: prefer taking/approaching resources where we are closer than opponent
    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    res_sorted = sorted(resources, key=lambda c: cheb(sx, sy, c[0], c[1]))
    targets = res_sorted[:3]  # keep it cheap

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh): 
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        for tx, ty in targets:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Encourage being closer; strong bonus for stepping onto a resource
            take_bonus = 30 if (nx, ny) == (tx, ty) else 0
            val += take_bonus + (d_opp - d_self) * 3 - d_self
        # Mildly prefer moves that reduce distance to any resource (diversifies between ties)
        min_d = min(cheb(nx, ny, tx, ty) for tx, ty in resources)
        val -= min_d * 0.1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]