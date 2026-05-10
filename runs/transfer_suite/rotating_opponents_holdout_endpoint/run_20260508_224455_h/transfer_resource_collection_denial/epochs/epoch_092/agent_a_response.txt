def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        dx = dx if dx >= 0 else -dx
        dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        return [0, 0]

    # Prefer immediate resource capture; otherwise move to best "contested" target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in obs:
                continue

            d_ours = dist8(nx, ny, rx, ry)
            d_opp = dist8(ox, oy, rx, ry)

            # If we can reach this immediately, do it.
            if d_ours == 0:
                val += 1000000
                continue

            # Competition: larger (opp - ours) means we are sooner.
            diff = d_opp - d_ours
            val += diff * 120

            # Secondary: closer is better, farther from being stuck is better.
            val += 40 / (1 + d_ours)

            # Slight preference for moving along the opponent's axis.
            val += (abs(ry - oy) - abs(ry - ny)) * 6

        # Obstacle-informed tie-break: discourage moves with fewer free neighbors.
        free_neighbors = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obs:
                free_neighbors += 1
        val += free_neighbors * 2

        # Keep value robust: avoid going nowhere if any contested target exists.
        if (dx, dy) == (0, 0):
            val -= 3

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]