def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy, ox, oy = int(s[0]), int(s[1]), int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    # If no resources visible, move to reduce distance to opponent (stall to avoid giving tempo).
    if not resources:
        best = (10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d < best[0]:
                best = (d, (dx, dy))
        return list(best[1])

    best_score = -10**18
    best_move = (0, 0)

    # Greedy 1-ply: choose next cell maximizing (how much closer we are than opponent) to a best resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Resource evaluation from this candidate next position.
        local_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Big weight on being ahead of opponent; then mildly prefer shorter my_d.
            score = (opp_d - my_d) * 10 - my_d
            if score > local_best:
                local_best = score

        # Small tie-break toward closer to the currently best resource.
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)
        elif local_best == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]