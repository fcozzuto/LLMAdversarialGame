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

    def bfs(start):
        qx, qy = [start[0]], [start[1]]
        dist = [[inf] * gh for _ in range(gw)]
        dist[start[0]][start[1]] = 0
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            d = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                    if d < dist[nx][ny]:
                        dist[nx][ny] = d
                        qx.append(nx); qy.append(ny)
        return dist

    sd = bfs((sx, sy))
    od = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        ds, do = sd[rx][ry], od[rx][ry]
        if ds >= inf:
            continue
        # Favor winning race: larger opponent advantage / smaller self distance
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best if best is not None else (sx, sy)
    if (sx, sy) == (rx, ry):
        return [0, 0]

    best_step = (0, 0)
    best_step_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
            continue
        nds, ndo = sd[nx][ny], od[nx][ny]
        # Reduce our distance while not allowing opponent to gain too much in the next step
        key = ( (ndo - nds) - (od[rx][ry] - sd[rx][ry]), -nds, -abs(rx - nx) - abs(ry - ny) )
        if best_step_key is None or key > best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]