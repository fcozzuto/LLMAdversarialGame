def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If already on a resource, stay deterministic but allow leaving if it improves contest.
    opp_to_res = None
    best = None

    # Strategic change: contest-first. Pick a move that maximizes how "ahead" we are relative to opponent
    # for the *best* remaining resource from our perspective (smaller my-opp distance difference is better).
    for dx, dy, nx, ny in legal:
        if resources:
            best_diff = None
            best_my = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                diff = myd - opd  # negative => we are closer to that resource
                if best_diff is None or diff < best_diff or (diff == best_diff and myd < best_my):
                    best_diff = diff
                    best_my = myd
            # Secondary objective: reduce our absolute distance to the contested resource
            myd_score = best_my
            # Tertiary: avoid moving adjacent to opponent (reduces chance of them taking nearby resources first)
            adj_pen = cheb(nx, ny, ox, oy)
            score = (best_diff, myd_score, adj_pen, dx, dy)
        else:
            # No resources left: move toward the farthest corner from opponent to secure tie-breaks.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far = -1
            for cx, cy in corners:
                far = max(far, cheb(cx, cy, ox, oy) - cheb(nx, ny, cx, cy))
            score = (-far, dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]