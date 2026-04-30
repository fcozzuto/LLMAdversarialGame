def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource that we can reach earlier than opponent, with safety and obstacle proximity.
    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    if resources:
        best_t = None
        best_tv = -10**18
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Main objective: win the resource by earlier arrival; tie-break with safety and staying near it.
            tv = (dop - dme) * 7.0 - dme * 0.6 - adj_obs(rx, ry) * 1.25
            # Mild bias to keep pressure toward opponent side.
            tv += 0.25 * cheb(rx, ry, w - 1, h - 1) - 0.25 * cheb(sx, sy, w - 1, h - 1)
            if tv > best_tv:
                best_tv = tv
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No resources visible: drift to opponent side while avoiding immediate obstacles.
        tx = (w - 1) if ox < w // 2 else 0
        ty = (h - 1) if oy < h // 2 else 0

    # Choose best immediate move via one-step lookahead scored by progress to target and denying opponent.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dme1 = cheb(nx, ny, tx, ty)
        dop1 = cheb(ox, oy, tx, ty)
        # If we move to reduce our distance, score rises; if opponent is closer, score drops.
        score = (dop1 - dme1) * 10.0 - dme1 * 0.9 - adj_obs(nx, ny) * 1.1
        # Encourage staying off the obstacle-adjacent tiles.
        score += 0.05 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves are blocked (rare), stay put.
    return best_move