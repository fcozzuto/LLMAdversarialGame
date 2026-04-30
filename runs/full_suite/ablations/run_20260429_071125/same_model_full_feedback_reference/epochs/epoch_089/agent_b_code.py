def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_dist(x0, y0, xt, yt):
        if (x0, y0) == (xt, yt):
            return 0
        if (xt, yt) in obstacles:
            return 10**9
        qx, qy = [x0], [y0]
        head = 0
        dist = {(x0, y0): 0}
        while head < len(qx):
            x, y = qx[head], qy[head]
            d = dist[(x, y)]
            head += 1
            nd = d + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if (nx, ny) not in dist:
                        if (nx, ny) == (xt, yt):
                            return nd
                        dist[(nx, ny)] = nd
                        qx.append(nx)
                        qy.append(ny)
        return 10**9

    # Choose a target resource where we have distance advantage over opponent.
    best = None
    best_t = resources[0]
    for rx, ry in resources:
        dmy = bfs_dist(sx, sy, rx, ry)
        dop = bfs_dist(ox, oy, rx, ry)
        # Prefer: (opponent farther than us), then smaller our distance, then deterministic tie.
        key = (dop - dmy, -dmy, -(rx + 3 * ry))
        if best is None or key > best:
            best = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Greedy: among legal deltas, pick move minimizing our BFS distance to target.
    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        d = bfs_dist(nx, ny, tx, ty)
        key = (d, (dx, dy))
        if best_d is None or key < (best_d, best_move):
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]