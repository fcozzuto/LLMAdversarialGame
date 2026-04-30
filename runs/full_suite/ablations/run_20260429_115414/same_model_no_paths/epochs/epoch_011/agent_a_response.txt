def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if o is not None and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_next_dist(px, py, tx, ty):
        best = None
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if inb(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if best is None or d < best:
                    best = d
        return best if best is not None else cheb(px, py, tx, ty)

    # Pick a resource where we have (opponent_dist - my_dist) advantage.
    best_r = None
    best_gain = None
    best_my = None
    for rx, ry in res:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        gain = op_d - my_d
        if best_r is None or gain > best_gain or (gain == best_gain and my_d < best_my):
            best_r = (rx, ry)
            best_gain = gain
            best_my = my_d

    rx, ry = best_r

    # Choose move that maximizes estimated advantage after both play greedily for that resource.
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_next = cheb(nx, ny, rx, ry)
        op_next = best_next_dist(ox, oy, rx, ry)
        # Prefer being closer; also prefer denying opponent by increasing their remaining distance relative to ours.
        score = (op_next - my_next) * 10 - my_next
        # Mild tie-break toward moving generally toward the target.
        score -= (abs((nx - rx)) + abs((ny - ry))) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]