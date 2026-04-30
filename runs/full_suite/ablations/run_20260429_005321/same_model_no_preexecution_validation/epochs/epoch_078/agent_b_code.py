def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def near_obs_score(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    def pick_target():
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]; bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer, and with shorter absolute time.
            # Penalize being next to obstacles to reduce pathing traps.
            v = (d_op - d_me) * 3.0 - d_me * 0.5 - near_obs_score(rx, ry) * 0.6
            # Small deterministic tie-break
            v += (-(rx + 1) * 0.001 - (ry + 1) * 0.0007)
            if v > bestv:
                bestv = v; best = (rx, ry)
        return best

    tx, ty = pick_target()

    # Evaluate candidate moves toward target with opponent pressure and obstacle avoidance.
    best_move = (0, 0); best_score = -10**18
    cur_t = cheb(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # progress + safety; slight preference to keep moving if progress is non-worse.
        prog = cur_t - d_me
        safety = -near_obs_score(nx, ny) * 0.7
        # Try to avoid giving opponent an easier route to the same target by moving only when we improve lead.
        lead = (d_op - d_me)
        score = prog * 4.0 + lead * 1.1 + safety + (1.0 if (dx != 0 or dy != 0) else 0.0) * 0.05
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]