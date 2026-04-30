def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def bfs(start):
        dist = [[10**9] * h for _ in range(w)]
        q = [start]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        if d < dist[nx][ny]:
                            dist[nx][ny] = d
                            q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_res = None
    best_adv = -10**18
    for rx, ry in resources:
        md = myd[rx][ry]
        od = opd[rx][ry]
        if md >= 10**9 and od >= 10**9:
            continue
        adv = (od - md)
        if adv > best_adv or (adv == best_adv and (best_res is None or md < myd[best_res[0]][best_res[1]])):
            best_adv = adv
            best_res = (rx, ry)

    if best_res is None:
        moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        bx, by = sx, sy
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if opd[nx][ny] > opd[bx][by] or (opd[nx][ny] == opd[bx][by] and (nx + ny) < (bx + by)):
                    bx, by = nx, ny
        return [bx - sx, by - sy]

    rx, ry = best_res
    best_move = (0, 0)
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            my_dist = myd[nx][ny]
            if my_dist >= 10**9:
                continue
            my_to_res = my_dist
            opp_to_res = opd[rx][ry]
            opp_after = opd[nx][ny]
            opp_cur = opd[ox][oy]
            score = -my_to_res
            score += 0.18 * (opp_to_res - opd[nx][ny])
            score += 0.06 * (opp_cur - opp_after)
            score += 0.02 * (abs(nx - ox) + abs(ny - oy))
            if nx == rx and ny == ry:
                score += 1000
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]