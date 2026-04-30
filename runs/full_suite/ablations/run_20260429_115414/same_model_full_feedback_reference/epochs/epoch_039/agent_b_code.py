def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        for dx, dy in ((0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    best_step = (0, 0)
    best_val = -10**18

    steps = ((-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            # Choose the move that maximizes "resource advantage"
            # advantage = (op_dist - self_dist) - small bias toward closeness
            step_val = -10**18
            for rx, ry in resources:
                dself = king_dist(nx, ny, rx, ry)
                dop = king_dist(ox, oy, rx, ry)
                val = (dop - dself) * 2 - dself
                if val > step_val:
                    step_val = val
            if step_val > best_val:
                best_val = step_val
                best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]