def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    role = (observation.get("self_role") or "").lower()
    self_is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("coward" in role)
    opp_is_evader = not self_is_evader

    def greedy_step(x, y, tx, ty, want_increase):
        best = None
        best_move = (0, 0)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if blocked(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            val = d if want_increase else -d
            if best is None or val > best:
                best = val
                best_move = (dx, dy)
        return best_move[0], best_move[1]

    # 1-ply lookahead: we pick our move, opponent then responds greedily to chase (or evade) us.
    want_increase_for_us = self_is_evader
    best_score = None
    best_move = (0, 0)
    for mdx, mdy in dirs:
        nx, ny = sx + mdx, sy + mdy
        if blocked(nx, ny):
            continue
        # Opponent greedy response against our new position (assume opposite objective)
        odx, ody = greedy_step(ox, oy, nx, ny, opp_is_evader)
        nox, noy = ox + odx, oy + ody
        if blocked(nox, noy):
            nox, noy = ox, oy
        d_after = cheb(nx, ny, nox, noy)
        score = d_after if want_increase_for_us else -d_after
        if best_score is None or score > best_score:
            best_score = score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]