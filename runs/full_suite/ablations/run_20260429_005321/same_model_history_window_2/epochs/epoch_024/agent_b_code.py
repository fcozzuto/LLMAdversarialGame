def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = moves

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obst:
                pen += 1
        return pen

    def best_target_from(x, y):
        if not resources:
            return None, 0
        best_d = 10**9
        best = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best_d:
                best_d = d
                best = (rx, ry)
        return best, best_d

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        target, dres = best_target_from(nx, ny)
        dopp = cheb(nx, ny, ox, oy)

        # Primary: get closer to nearest resource.
        # Secondary: prefer moves that keep distance from opponent.
        # Tertiary: avoid moves adjacent to obstacles.
        pen = obst_adj_pen(nx, ny)
        score = -dres * 100 + dres  # tie-breaker closer better
        score += dopp * 2
        score -= pen * 3

        # If standing on a resource (allowed), prioritize heavily.
        if target is not None and (nx, ny) == target:
            score += 100000

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]