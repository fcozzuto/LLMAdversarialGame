def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    # Pick best resource by guaranteed advantage and closeness.
    best = None
    best_score = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF:
            continue
        # Higher is better: (opponent later) + (we're closer)
        adv = (do - ds)
        score = adv * 10 - ds
        # Tie-break deterministically toward lower coordinates
        tie = (rx * 100 + ry)
        if score > best_score or (score == best_score and (best is None or tie < best[0] * 100 + best[1])):
            best_score = score
            best = (rx, ry)

    # If no resources, head to center deterministically.
    if best is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = best

    # Choose move that approaches target while not giving opponent an immediate advantage.
    cur_ds = dS[sx][sy]
    best_move = (0, 0)
    best_move_score = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Decrease distance to target; reward when we maintain/extend advantage.
        ns = dS[nx][ny]
        nd_target = dS[tx][ty]  # constant-ish but keep for determinism
        # Estimate "who gets target first" from next states
        estS = ns
        estO = dO[tx][ty]  # opponent distance to target is static
        # small bias for moving toward target
        toward = -(abs(nx - tx) + abs(ny - ty))
        move_score = (estO - estS) * 10 - estS + toward
        # Secondary tie-break: smallest dx, then dy in order of moves list already deterministic.
        if move_score > best_move_score or (move_score == best_move_score and (dx, dy) == (0, 0) and best_move != (0, 0)):
            best_move_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]