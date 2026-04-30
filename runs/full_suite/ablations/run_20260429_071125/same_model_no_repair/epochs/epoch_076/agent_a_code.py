def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    oxp, oyp = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    def obstacle_penalty(x, y):
        # Small penalty for moving close to obstacles; avoids obstacle hits/near-grazes.
        pen = 0
        for ox, oy in obstacles:
            d = cheb(x, y, ox, oy)
            if d == 0:
                return 1e9
            if d == 1:
                pen += 0.6
            elif d == 2:
                pen += 0.2
        return pen

    # Targeting strategy changes: avoid greedy 1-step Manhattan; use chebyshev and opponent pressure.
    corners = [(0, 0), (w - 1, h - 1), (0, h - 1), (w - 1, 0)]
    if resources:
        # Deterministic: pick a resource with minimal (chebyshev distance + tie-break by relative ordering).
        best = None
        best_key = None
        for rx, ry in resources:
            key = (cheb(sx, sy, rx, ry), abs(rx - oxp) + abs(ry - oyp), ry, rx)
            if best_key is None or key < best_key:
                best_key, best = key, (rx, ry)
        tx, ty = best
        # Also discourage giving opponent easy access by preferring moves that increase opponent-cheb distance.
        opp_w = 0.08
        res_w = 1.0
        pos_w = 0.003
    else:
        # Roam: deterministically head to the corner farthest from opponent.
        best_corner = None
        best_key = None
        for cx, cy in corners:
            key = (-cheb(cx, cy, oxp, oyp), cy, cx)
            if best_key is None or key < best_key:
                best_key, best_corner = key, (cx, cy)
        tx, ty = best_corner
        opp_w = 0.12
        res_w = 0.7
        pos_w = 0.002

    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        d_res = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, oxp, oyp)
        # Prefer closer to target, but keep away from obstacles; also slightly prefer pushing away opponent.
        score = res_w * d_res + obstacle_penalty(nx, ny) - opp_w * d_opp + pos_w * (nx + 3 * ny)
        if best_score is None or score < best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]