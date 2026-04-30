def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Evaluate each move by how much it improves our lead for the best target next.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Choose best target resource for this prospective position.
        move_best = -10**18
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            od = king_dist(ox, oy, rx, ry)
            # Lead-first; then reduce our distance; slight preference for nearer resources.
            val = (od - sd) * 100 - sd - (rx + ry) * 0.0001
            if val > move_best:
                move_best = val

        # Discourage stepping into dead-ends behind obstacles (small penalty if very close to obstacle)
        neigh_pen = 0
        for px in (nx - 1, nx, nx + 1):
            for py in (ny - 1, ny, ny + 1):
                if (px, py) in obs:
                    neigh_pen += 2
        score = move_best - neigh_pen * 0.5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]