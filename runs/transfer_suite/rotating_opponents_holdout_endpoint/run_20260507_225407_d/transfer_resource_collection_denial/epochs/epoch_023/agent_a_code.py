def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inf = 10**9

    def bfs(st):
        dist = [[inf] * gh for _ in range(gw)]
        x0, y0 = st
        if 0 <= x0 < gw and 0 <= y0 < gh and (x0, y0) not in obstacles:
            dist[x0][y0] = 0
        qx = [x0]
        qy = [y0]
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                    if nd < dist[nx][ny]:
                        dist[nx][ny] = nd
                        qx.append(nx)
                        qy.append(ny)
        return dist

    sd = bfs((sx, sy))
    od = bfs((ox, oy))

    best = None
    best_key = None
    # Prefer resources where we arrive earlier; break ties by arriving sooner, then farther from opponent.
    for rx, ry in resources:
        myd = sd[rx][ry]
        if myd >= inf:
            continue
        opd = od[rx][ry]
        if opd >= inf:
            opd = 0  # if opponent unreachable, treat as 0 distance advantage for us
        key = (myd - opd, myd, -(abs(rx - ox) + abs(ry - oy)), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    curd = sd[sx][sy]
    best_move = (0, 0)
    best_next = inf
    # Deterministically step along decreasing sd towards target (avoid obstacles and stay-in-place if needed).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
            continue
        nd = sd[nx][ny]
        if nd < best_next or (nd == best_next and (dx, dy) < best_move):
            best_next = nd
            best_move = (dx, dy)

    # If all candidates are inf (shouldn't happen), just move toward target clamped.
    if best_next >= inf:
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # If we're already at the target or cannot improve distance, still return a valid move (best_move may be (0,0)).
    return [best_move[0], best_move[1]]