def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def dist_to_best(x, y, targets):
        if not targets:
            return 10**9
        best = 10**9
        for tx, ty in targets:
            d = cheb(x, y, tx, ty)
            if d < best:
                best = d
        return best

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    our_base = dist_to_best(sx, sy, resources)
    opp_base = dist_to_best(ox, oy, resources)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        our_d = dist_to_best(nx, ny, resources)
        opp_d = opp_base if not resources else dist_to_best(ox, oy, resources)
        val = (opp_d - our_d)
        if resources:
            val += 0.05 * cheb(nx, ny, sx, sy) * (-1)
        if (nx, ny) == (ox, oy):
            val -= 1000
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    nx, ny = sx + best_move[0], sy + best_move[1]
    if not valid(nx, ny):
        return [0, 0]
    return best_move