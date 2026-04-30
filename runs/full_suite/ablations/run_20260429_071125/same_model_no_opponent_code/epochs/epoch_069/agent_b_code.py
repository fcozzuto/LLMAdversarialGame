def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        tx, ty = (w - 1 if sx < ox else 0), (h - 1 if sy < oy else 0)
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def nearest_dist(x, y, take_farthest):
        best = None
        for rx, ry in resources:
            d = md(x, y, rx, ry)
            if best is None:
                best = d
            else:
                if take_farthest:
                    if d > best: best = d
                else:
                    if d < best: best = d
        return best if best is not None else 0

    take_farthest = (int(observation.get("turn_index") or 0) % 2 == 1) and (len(resources) >= 3)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        my_next = nearest_dist(nx, ny, take_farthest)
        opp_next = nearest_dist(ox, oy, take_farthest)

        # Contention: favor states where we are strictly closer to some resource than opponent.
        # Bonus if we step toward the "front" of the resource set near us.
        contention = (opp_next - my_next)

        # Obstacle/wall pressure: penalize moves that reduce local freedom.
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                free += 1

        # Mild preference for progress toward bottom-right quadrant (deterministic tie-break).
        quad_bias = (nx + ny)

        val = 3.0 * contention + 0.15 * free - 0.01 * my_next + 0.0001 * quad_bias
        if val > best_val:
            best_val = val
            best_move = [int(nx - sx), int(ny - sy)]

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [dx, dy]