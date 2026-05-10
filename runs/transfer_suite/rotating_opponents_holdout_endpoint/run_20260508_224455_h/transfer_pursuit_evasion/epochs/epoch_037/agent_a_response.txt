def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "escape"))
    target_x, target_y = ox, oy

    # depth-limited BFS distances to target with obstacle avoidance (deterministic)
    maxd = 6
    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    if 0 <= target_x < w and 0 <= target_y < h and (target_x, target_y) not in obs:
        dist[target_x][target_y] = 0
        q = [(target_x, target_y)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d0 = dist[x][y]
            if d0 >= maxd:
                continue
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] > d0 + 1:
                    dist[nx][ny] = d0 + 1
                    q.append((nx, ny))

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # avoid immediate "capture position" when acting as pursuer (if roles are swapped, this is still safe as it just changes preference)
        if not is_evader and nx == ox and ny == oy:
            val = 0 if dist[nx][ny] == 0 else -1
            # capture is good; take it
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
            continue
        man = abs(nx - ox) + abs(ny - oy)
        d_to_target = dist[nx][ny]
        if is_evader:
            # maximize distance; also avoid being in cells with known short path to opponent
            val = (man * 10) + (d_to_target if d_to_target < INF else maxd + 1)
            # slight preference to move away from the nearest obstacle
            if obs:
                ne = INF
                for ax, ay in obs:
                    dd = abs(nx - ax) + abs(ny - ay)
                    if dd < ne: ne = dd
                val += ne
        else:
            # minimize distance-to-opponent path estimate
            val = -(d_to_target if d_to_target < INF else (man + maxd)) - man
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]