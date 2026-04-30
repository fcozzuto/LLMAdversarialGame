def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def local_obs_pen(x, y):
        c = 0
        for ddx, ddy in dirs:
            if (x + ddx, y + ddy) in obstacles:
                c += 1
        return c

    def best_from(x, y):
        if not resources:
            # Go roughly toward center, but also away from obstacles a bit
            cx, cy = w // 2, h // 2
            return -cheb(x, y, cx, cy) - 0.2 * local_obs_pen(x, y)
        bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(x, y, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            v = (d_op - d_me) * 3.2 - 0.25 * d_me
            if (rx, ry) == (x, y):
                v += 1e6
            # Mild bias to avoid repeatedly oscillating near opponent
            d_opp = cheb(x, y, ox, oy)
            v += 0.02 * d_opp
            v -= 0.08 * local_obs_pen(x, y)
            if v > bestv:
                bestv = v
        return bestv

    # One-step lookahead: choose the move that maximizes best_from(next)
    best_moves = []
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sc = best_from(nx, ny)
        if sc > best_score + 1e-12:
            best_score = sc
            best_moves = [(dx, dy)]
        elif abs(sc - best_score) <= 1e-12:
            best_moves.append((dx, dy))

    # Deterministic tie-break: prefer staying still last, then lower dx, then lower dy
    # (keeps behavior stable and avoids random drift)
    if not best_moves:
        return [0, 0]
    best_moves.sort(key=lambda d: (d[0] == 0 and d[1] == 0, d[0], d[1]))
    return [int(best_moves[0][0]), int(best_moves[0][1])]