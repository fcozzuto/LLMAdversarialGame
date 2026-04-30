def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(start):
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles: return dist
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    legal_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal_moves.append((dx, dy))

    if not resources:
        return [0, 0] if (0, 0) not in legal_moves else [0, 0]

    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        d0 = our_dist[ry][rx]
        d1 = opp_dist[ry][rx]
        if d0 >= INF and d1 >= INF: 
            continue
        # Prefer resources we can reach; if both reachable, maximize (opp - our).
        # Tie-break by earlier our distance and deterministic coord order.
        if d0 < INF:
            reach = 1
        else:
            reach = 0
        if d1 < INF:
            reach_opp = 1
        else:
            reach_opp = 0
        if reach == 0 and reach_opp == 1:
            continue
        if d0 >= INF:  # only reachable by opponent (both can't be INF due to earlier continue)
            continue
        adv = d1 - d0
        val = adv * 1000 + (INF - d0) + (3 if rx < w // 2 else 0) - (ry if rx + ry else 0)
        if best_r is None or val > best_val or (val == best_val and (rx, ry) < best_r):
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0] if (0, 0) in legal_moves else [legal_moves[0][0], legal_moves[0][1]]

    tx, ty = best_r
    curd = our_dist[sy][sx]
    # Move to neighbor with minimal distance to target; deterministic tie-break by dx,dy order.
    candidates = []
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        nd = our_dist[ny][nx]
        if nd < INF:
            candidates.append((nd, dx, dy))
    if not candidates:
        return [0, 0] if (0, 0) in legal_moves else [legal_moves[0][0], legal_moves[0][1]]

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    # If already optimal (including possible stay), choose accordingly.
    return [int(dx), int(dy)]