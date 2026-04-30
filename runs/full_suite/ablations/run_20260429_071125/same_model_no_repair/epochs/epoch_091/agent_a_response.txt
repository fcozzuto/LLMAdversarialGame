def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_from(startx, starty):
        INF = 10**9
        if not inb(startx, starty):
            return None
        dist = [[INF] * h for _ in range(w)]
        qx, qy = [startx], [starty]
        qi = 0
        dist[startx][starty] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves[:9]:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    my_dist = dist_from(sx, sy)
    op_dist = dist_from(ox, oy)

    best = None
    best_score = 10**18
    for rx, ry in resources:
        md = my_dist[rx][ry] if my_dist else 10**9
        od = op_dist[rx][ry] if op_dist else 10**9
        if md >= 10**8:
            continue
        # Prefer reachable resources where we are earlier; penalize if opponent is significantly closer.
        score = md + (0 if od >= 10**8 else (max(0, od - md) * -0.15)) + (0 if od >= 10**8 else (max(0, md - od) * 0.6))
        # Small deterministic tie-break toward resources closer to bottom-right (any fixed bias).
        score += (rx + 1) * 0.001 + (ry + 1) * 0.002
        if score < best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    rx, ry = best
    if (sx, sy) == (rx, ry):
        return [0, 0]

    target_dist = my_dist[rx][ry]
    best_move = (0, 0)
    best_step_score = 10**18
    for dx, dy in moves[:9]:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = my_dist[nx][ny]
        if d >= target_dist:
            continue
        # Prefer moves that reduce our distance the most toward target.
        step_score = (d - (target_dist - 1)) * 10 + (abs(nx - rx) + abs(ny - ry)) * 0.01
        if step_score < best_step_score:
            best_step_score = step_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]